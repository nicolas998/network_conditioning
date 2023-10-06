import numpy as np 
import argparse
import geopandas as gp 

parser = argparse.ArgumentParser(description='Using the hillslopes and the ranks generates a numpy lut file used to create binary files')
parser.add_argument('hills',type=str, help = 'path to the hills vector')
parser.add_argument('ranks',type=str, help = 'path to the vector with the ranks')
parser.add_argument('lut',type=str, help = 'path to the numpy file with the lids, ranks, and weigths')
args = parser.parse_args()

# execute if main 
if __name__=='__main__':
    
    #Reads the hillslopes and ranks 
    h = gp.read_file(args.hills)
    r = gp.read_file(args.ranks)

    #Makes the union between both
    union = gp.overlay(h, r, how='intersection', )
    union['area_r'] = union.area
    union.set_index('LINKNO', inplace = True)

    #Gets the weigth
    lids = union.index.values
    ranks = union['rank'].values
    areas = union['area_r'].values
    w = np.zeros(union.shape[0])
    for lid in np.unique(lids):
        p = np.where(lids == lid)
        w[p] = areas[p]/areas[p].sum()
        
    #Save the lut in a npz file 
    lut_dtype = np.dtype(
        [
            ('lid', np.int32),
            ('xy1d', np.int32),
            ('weight', np.float32)
        ]
    )
    sorter = np.argsort(lids)    
    rec = np.core.records.fromarrays(
        (
            np.asarray(lids)[sorter],
            np.asarray(ranks)[sorter],
            np.asarray(w)[sorter]
        ),
        dtype=lut_dtype
    )
    np.save(args.lut, rec)