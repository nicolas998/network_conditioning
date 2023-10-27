import geopandas as gp 
import numpy as np 
from shapely import geometry, ops 
from shapely.geometry import LineString, mapping
import glob
from multiprocessing import Pool
import argparse
import pandas as pd
import os 

parser = argparse.ArgumentParser(description='Takes the networks from IFIS HD, applies the upstream area threshold and merges adjacent links')
parser.add_argument('in_path',type=str, help = 'original network')
parser.add_argument('out_path',type=str, help = 'network with the output')
parser.add_argument('min_area',help = 'minimum threshold area to define network', type = float)
parser.add_argument('min_len',help = 'minimum lenght of the links to define if they must be (or not) joined', type = float)
parser.add_argument('simplify',help = 'simplification threshold for the ogr2ogr function', type = float)
args = parser.parse_args()

def main(path, area, len):
    
    def simplify_line(line, tolerance):
        if line.geom_type == 'LineString':
            return line.simplify(tolerance)
        else:
            return line
    
    def round_coordinates(line):
        if isinstance(line, LineString):
            return LineString([(round(x, 7), round(y, 7)) for x, y in line.coords])
        return line
    
    #Functions that merges the network 
    def merge_streams(link, length_min = 800):
        #Get the properties of the link
        length = n.loc[link, 'Length']
        lines = [n.loc[link,'geometry']]    
        link_area = n.loc[link, 'DSContArea']
        try:
            l = n.loc[link, 'ds']
            area = n.loc[l, 'DSContArea']
        except:
            area = n.loc[link, 'DSContArea']
        #Updates the global list with the links already processed
        proccessed.append(link)
        while length < length_min:#and area/link_area<1.1:
            #try:
            #Exists if reach an outlet 
            if n.loc[link, 'ds']==0:
                print('link %d out of bounds' % link)
                return link, length, ops.linemerge(geometry.MultiLineString(lines))
            #Exists if the downstream has two parents
            if n.loc[n.loc[link, 'ds'], 'parents']>1:
                print('link %d has more than one parent' % link)
                return link, length, ops.linemerge(geometry.MultiLineString(lines))
            #Adds the following link to the list
            link = n.loc[link, 'ds']
            lines.append(n.loc[link,'geometry'])            
            length += n.loc[link, 'Length']            
            #Updates the global list with the links already processed
            proccessed.append(link)
            # except:
            #     print('no downstream')
            #     #Exists if there is no downstream link (must not happen)
            #     return link, length, ops.linemerge(geometry.MultiLineString(lines))
        #Exist if the total lenght > lenght_min
        return link, length, ops.linemerge(geometry.MultiLineString(lines))
    
    #Reads the original network 
    print('Step 1: start, reading network, may take some time ...')
    n = gp.read_file(args.in_path)
    n = n.loc[n['DSContArea'] > args.min_area]
    n = n.sort_values('DSContArea')
    n.set_index('LINKNO', inplace = True)
    #Get the parent list for the new network 
    print('Step 1: getting number of parents for the new network ...')
    n['parents'] = 0
    for link in n.index:
        link = n.loc[link, 'ds']
        if link > 0:
            n.loc[link,'parents']+=1
    
    print('Step 1: finished. Network readed, processing links with area > %.1f' % args.min_area)
    
    #Creates one merged network
    if args.min_len > 0:
        print('Step 2: Start. merging streams to obtain lengths greater than %.1f' % args.min_len)
        n2 = []
        geometries = []
        proccessed = []
        for link in n.index:
            if link not in proccessed:
                if n.loc[link, 'Length'] < args.min_len:
                    link, length, geom = merge_streams(link, args.min_len)
                    n2.append([link, length])
                    geometries.append(geom)        
                else:
                    n2.append([link, n.loc[link, 'Length']])
                    geometries.append(n.loc[link, 'geometry'])
                    proccessed.append(link)
        print('Step 2: Update. Merging finished')
        n2 = gp.GeoDataFrame(n2, geometry=geometries, crs=n.crs)    
        n2.rename(columns={0:'LINKNO', 1:'length'}, inplace = True)
    else:
        print('Step 2: skiped, no merging downstream using lengths as they are.')    
        n2 = n[['LINKNO','geometry']]

    print('Step 3: Start simplifying, rounding coordinates, and save.')        
    #Simplify the geometry     
    n2['geometry'] = n2['geometry'].apply(lambda geom: simplify_line(geom, args.simplify))
    n2 = n2.to_crs(epsg=4326)
    n2.geometry = n2.geometry.apply(round_coordinates)
    # Save the GeoPandas DataFrame to a JSON file in GeoJSON format
    n2.to_file(args.out_path, driver='GeoJSON')
    print('Step 3: Finish, geojson saved at %s' % args.out_path)

if __name__ == "__main__":
    main(args.out_path, args.min_area, args.min_len)