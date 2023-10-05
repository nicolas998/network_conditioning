import numpy as np 
import argparse
import raster_functions as rasf

parser = argparse.ArgumentParser(description='Takes aqn original image of a forcing and its sliced version and creates a rank matrix')
parser.add_argument('image',type=str, help = 'path to the original image')
parser.add_argument('slice',type=str, help = 'path to the sliced image')
parser.add_argument('ranks',type=str, help = 'path to image with the ranks')
args = parser.parse_args()

# execute if main 
if __name__=='__main__':
    
    # reads the original and the sliced image 
    original, prop_o, epsg = rasf.read_raster(args.image)
    sliced, prop_s, epsg = rasf.read_raster(args.slice)
    
    #Get the localization properties of the slice
    Cb, Ca, Rb, Nr1 = rasf.get_slice_location(prop_o, prop_s)
    
    #Get the rank matrix
    ranks = np.arange(0, original.size)
    ranks = ranks.reshape(original.shape)

    #Sve a tif map with the ranks 
    ranks_slice = ranks[Rb:Rb+Nr1, Cb:Ca]
    rasf.save_array2raster(ranks_slice, args.ranks, prop_s)
    
    