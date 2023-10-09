#!/local/miniconda3/bin/python
from sys import path as sysPath
from os import path

from time import time
from datetime import datetime, timedelta
from calendar import timegm
from glob import glob
import numpy as np
from multiprocessing import Pool

from osgeo import gdal
gdal.DontUseExceptions()


from config import *
from bin import save_bin


sysPath.append(
    path.join(
        path.dirname(__file__),
        "..",
        "common"
    )
)

from gridlid import convert
from common import *

versions = {
    "v0": {"dir": "GaugeCorr_QPE_01H",          "pref": "GaugeCorr_QPE_01H"},
    "v1": {"dir": "MultiSensor_QPE_01H_Pass2",  "pref": "MultiSensor_QPE_01H_Pass2"}
}

def fnOld2fnNew(fn):
    return fn.replace(
        versions['v0']['pref'],
        versions['v1']['pref']
    )

def main(fn):
    print (fn, end="")
    try:
        dt = datetime.strptime(
            'MRMS_' + fnOld2fnNew(path.basename(fn)),
            fn_template[:-3]
        )
    except:
        print (" ---> wrong date")
        return
    uxt = timegm(dt.timetuple())
    out_fn = path.join(
        out_dir.format(yr=str(dt.year)), str(uxt)
    )
    if path.exists(out_fn):
        print (" skip")
        return
    try:
        grib = gdal.Open(fn)
        _lids, _vals, _cnt =  convert(grib.GetRasterBand(1).ReadAsArray().ravel(), lut)
        grib = None
        del grib
    except:
        print (" ---> bad grib")
        return
    print(" done")
    if _cnt < 1:
        return
    save_bin(_lids, _vals, out_fn)
    return



lut_src  = r"W:\HLM_plus_v2023\lut_mrms.npy"
lut = np.load(src_lut)

yr = 2020
input_dir   =  r"Z:\mrs\hlm\MRMS\{yr}\*\*\*.grib2"         #  "/nfs/mrs/hlm/MRMS"
out_dir     =  r"W:\HLM_plus_v2023\bin_mrms\{yr}".format(yr=yr)



assignments = sorted(
    glob(
        input_dir.format(yr=yr)
    )
)
# assignments = [a for a in assignments if a.split("/")[6] != '01']
t0 = time()
print (assignments)

if __name__ == "__main__":
    # for a in assignments:
    #     main(a)
    pool = Pool(7)
    pool.map(main, assignments)
    pool.close()
    pool.join()



print (
    path.basename(__file__),
    time() - t0
)


