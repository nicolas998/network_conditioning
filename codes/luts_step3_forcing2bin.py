import numpy as np 
import argparse
import glob

parser = argparse.ArgumentParser(description='Using the luts from step2 and the forcing, creates a binary file')
parser.add_argument('lut',type=str, help = 'path to the numpy file with the lids, ranks, and weigths')
parser.add_argument('date',type=str, help = 'date to explore data in the format: YYYY/MM/DD')
parser.add_argument('out_folder',type=str, help = 'Folder to save the binary files')
parser.add_argument('-f', '--folder',type=str, help = 'Folder with the forcing data')
args = parser.parse_args()

# execute if main 
if __name__=='__main__':
    
    #Read the luts
    lut = np.load(args.lut)
    lids = lut['lid']
    
    #List the files for the given date
    glob.glob('')
    
    