from struct import pack
import io
from datetime import datetime, timezone
from raster_functions import *
import numpy as np 

#Function to convert MRMS filenames format to date and return the unix time
def MRMStime2unix(file):
    return int(datetime.strptime(file.split('_')[-1][:-10], '%Y%m%d-%H').replace(tzinfo=timezone.utc).timestamp())

#Function to sum the vals using the positions 
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

def file2vals(file, threshold, out_path , lut, timeConversion = MRMStime2unix):
    #Reads the forcing and converts it to the hill shape
    vals, prop, epsg = read_raster(file)
    vals = vals.reshape(vals.size)
    w_vals = vals[lut['xy1d']] * lut['weight']
    
    #Sum the values for each link
    ulids, val = grp_sum(w_vals, lut['lid'])
    
    #Writes a binary file 
    p = np.where(val > threshold)
    unix = timeConversion(file)
    #Saves if there is at least 5% of coverage
    if val[p].size/ulids.size > 0.01:
        saveBin(ulids[p], val[p], val[p].size, out_path+str(unix))