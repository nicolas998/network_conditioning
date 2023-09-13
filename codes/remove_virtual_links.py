import network_functions as netf
import argparse

parser = argparse.ArgumentParser(description='Takes a network written by TauDEM and removes the links that have no geometrical representation')
parser.add_argument('net',type=str, help = 'path to the shp file with the TauDEM network')
parser.add_argument('out',type=str, help = 'path to the shp file with the edited network')
parser.add_argument('--maxnpar','-n', type=float, help = 'Extra meters to add to the log(a) where a is the upstream area', default = 10)
args = parser.parse_args()


if __name__=='__main__':
    #Reads the network
    n = netf.gp.read_file(args.net)
    #Remove the ghost parents 
    n = netf.binary2multiple_parents(n, max_nparents = args.maxnpar)
    #Saves the new network
    n.to_file(args.out)

