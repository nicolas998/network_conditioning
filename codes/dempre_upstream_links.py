import network_functions as netf
import argparse

parser = argparse.ArgumentParser(description='Takes a network written by TauDEM and removes the links that have no geometrical representation')
parser.add_argument('net',type=str, help = 'path to the table of the network')
parser.add_argument('lid',type=int, help = 'linkid of the watershed outlet')
parser.add_argument('out',type=str, help = 'path to the table with the links that belong to the subwatershed')
#parser.add_argument('--maxnpar','-n', type=float, help = 'Extra meters to add to the log(a) where a is the upstream area', default = 10)
args = parser.parse_args()

if __name__=='__main__':
    #Reads the network
    n = netf.pd.read_csv(args.net, index_col = 1)
    #Get subwatershed
    n = netf.get_subwatershed(n, args.lid)
    #Saves the new network
    n.reset_index()[['LINKNO']].to_csv(args.out)