import geopandas as gp 
import numpy as np 
import argparse
import network_functions as netf

parser = argparse.ArgumentParser(description='Takes a network proccessed with remove_virtual_links.py and builds the rvr for hlm, if linkid is None (default) the rvr will correspond to the while network')
parser.add_argument('net',type=str, help = 'path to the shp file with the nhd network')
parser.add_argument('out',type=str, help = 'path to the outlet rvr')
parser.add_argument('--linkid','-l', type=int, help = 'Outlet link of the watershed to extract the network from', default = None)
parser.add_argument('--listlids','-a', type=str, help = 'plain text file with the list of links to extract rvrs, it will write with their lid as nates to the designed path', default = None)
args = parser.parse_args()

if __name__=='__main__':
    #Reads the network
    net = netf.gp.read_file(args.net)
    #takes subnet if needed 
    if args.listlids is None:
        if args.linkid is not None:
            net = netf.get_subwatershed(net, args.linkid)
            name = '%s/%d.rvr' % (args.out, args.linkid)
            netf.hlm_write_rvr(net, name)
        else:
            name = '%s' % args.out
            netf.hlm_write_rvr(net, name)
    else:
        print('args.listlids has not been implemented yet')
    
    
    
