from osgeo import gdal
from uuid import uuid4
from glob import glob
import geobuf
import json
from os import system, path, makedirs, unlink
gdal.UseExceptions()
from multiprocessing import Pool

def geo2pbf(fn):
    with open(fn) as f: geojson = json.loads(f.read())
    pbf = geobuf.Encoder().encode(geojson)
    unlink (fn)
    fn = fn.replace('geojson', 'pbf')
    with open(fn, "wb") as f: f.write(pbf)


def pbf2json(pbf_fn):
    ds = gdal.OpenEx(pbf_fn, gdal.OF_VECTOR)  # note use of gdal.OpenEx, ogr is deprecated from gdal 2.0+
    output = pbf_fn.replace('pbf', 'geojson')
    gdal.VectorTranslate(output, ds)
    return output

def main(src):
    bname = path.basename(src)
    dst = src.replace(
        bname, bname.replace(".pbf", ".geojson")
    ).replace('flood', 'flood_web')
    cmd = "ogr2ogr -s_srs EPSG:3857 -t_srs EPSG:4326 -overwrite -f GeoJSON {dst} {src}".format(
        src=src,
        dst=dst
    )
    if not path.isdir(path.dirname(dst)):
        makedirs(path.dirname(dst))
    print(cmd)
    if not path.isfile(dst): system(cmd)
    geo2pbf(dst)


#cmd_ogr = "/usr/bin/ogr2ogr -f GeoJSON -t_srs EPSG:4326  /home/web/inun/o_gjson /nfs/mrs/real_time/30Aug2021_07hr/{i_shp}"

cmd_cut = "/usr/local/bin/tippecanoe --minimum-zoom=8 --coalesce-smallest-as-needed --maximum-zoom=8 -f "
cmd_cut += "--projection=EPSG:4326 --no-simplification-of-shared-nodes --no-tile-stats --maximum-tile-bytes=20240 "
cmd_cut += "--output-to-directory /home/nicolas/network_conditioning/local_data/tiles/ /home/nicolas/network_conditioning/local_data/tiles/net_8z.json"
system(cmd_cut)

lst = glob('/home/nicolas/network_conditioning/local_data/tiles/*/*/*.pbf')
if __name__ == "__main__":
    pool = Pool(processes=4)
    pool.map(main, lst)
    pool.close()
    pool.join()