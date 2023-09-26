import geopandas as gp 
import numpy as np 
import argparse

parser = argparse.ArgumentParser(description='Takes an NHD network file and adds to it the column named: depth that will be used to burn the DEM')
parser.add_argument('nhd',type=str, help = 'path to the shp file with the nhd network')
parser.add_argument('--plus','-x', type=float, help = 'Extra meters to add to the log(a) where a is the upstream area', default = 10)
parser.add_argument('--multiply', '-y', type=float, help = 'multiplier used to expand the histogram', default = 1.25)
parser.add_argument('--minimum', '-m', type=float, help = 'minimum depth values for links with inf value', default = 1)
args = parser.parse_args()

n = gp.read_file(args.nhd)
n['log_area'] = n['VAA_DivDAS'].apply(lambda x: np.log(x))
n['depth'] = (n['log_area']+args.plus)*args.multiply
n.loc[np.isinf(n['depth']), 'depth'] = args.minimum
n.to_file(args.nhd)