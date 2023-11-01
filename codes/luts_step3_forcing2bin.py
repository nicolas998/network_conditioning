import numpy as np 
import argparse
import glob
import raster_functions as rastf

def HRRR_valeria_time2unix(file):
    return int(datetime.strptime(f.split('_')[1],'%Y%m%dT%H').replace(tzinfo=timezone.utc).timestamp())

def grp_sum(vals, lids):
    vals = vals.astype(np.float64)
    vals.cumsum(out=vals)
    inx = np.ones(len(lids), 'bool')
    inx[:-1] = lids[1:] != lids[:-1]
    unique_lids = lids[inx]
    vals = vals[inx]
    vals[1:] = vals[1:] - vals[:-1]
    return unique_lids, vals.astype(np.float32)

def saveBin(lid, lid_vals, count, fn):
    io_buffer_size = 4+4*100000
    lid = (lid)
    lid_vals = (lid_vals)
    fh = io.open(fn, 'wb', io_buffer_size)
    fh.write(pack('<I', count))
    for vals in zip(lid, lid_vals):
        fh.write(pack('<If', *vals))
    fh.close()

def saveTxt(lids, lid_vals, fn):
    f = open(fn, 'w')
    f.write('link, val\n')
    for lid,val in zip(lids, lid_vals):
        f.write('%d, %.2f\n' % (lid, val))
    f.close() 

def file2vals(file, threshold, out_path , ):#timeConversion = MRMStime2unix):
    #Reads the forcing and converts it to the hill shape
    vals, prop, epsg = rastf.read_raster(file)
    vals = vals.reshape(vals.size)
    w_vals = vals[lut['xy1d']] * lut['weight']
    
    #Sum the values for each link
    ulids, val = grp_sum(w_vals, lut['lid'])
    
    #Writes a binary file 
    p = np.where(val > threshold)
    unix = timeConversion(file, )
    saveBin(ulids[p], val[p], val[p].size, out_path)
    #saveTxt(ulids[p], val[p], out_path)

parser = argparse.ArgumentParser(description='Using the luts from step2 and the forcing, creates a binary file')
parser.add_argument('lut',type=str, help = 'path to the numpy file with the lids, ranks, and weigths')
parser.add_argument('in_folder',type=str, help = 'date to explore data in the format: YYYY/MM/DD')
parser.add_argument('out_folder',type=str, help = 'Folder to save the binary files')
parser.add_argument('-f', '--folder',type=str, help = 'Folder with the forcing data')
args = parser.parse_args()

# execute if main 
if __name__=='__main__':
    
    #Read the luts
    lut = np.load(args.lut)
    
    #List the files for the given date
    #glob.glob(args.in_folder)
    file2vals(args.in_folder, -9999, args.out_folder)
    
    