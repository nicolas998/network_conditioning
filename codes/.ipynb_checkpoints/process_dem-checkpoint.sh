#!/bin/sh
#$ -o out.txt
#$ -j y
#$ -cwd
#$ -pe 56cpn 224
####$ -l mf=16G
#$ -q IFC

module load stack/legacy
module use /Dedicated/IFC/.argon/modules
module load taudem
module load gdal/2.1.3_python-3.7.0

#variables 
npixels=900 # Upstream area to define network
dem=/Dedicated/IFC/Nicolas/iowa_hd/with_nhd_high/dem0708_clip_proj.tif
nhd=/Users/nicolas/2023_iowa_hd/maps/nhdPlus_h0708.shp
out=/Dedicated/IFC/Nicolas/iowa_hd/with_nhd_high

#Rasterizes the network
# gdal_calc.py --calc=A*0 --outfile=$out/network.tif -A $dem --overwrite
# gdal_rasterize -a depth $nhd $out/network.tif

# # #Burns the network into the DEM
gdal_calc.py --calc=A-B --outfile=$out/dem_burn.tif -A $dem -B $out/network.tif --overwrite 

# # Pitremove
mpiexec -n 224 pitremove -z $out/dem_burn.tif -fel $out/demfel.tif

# # D8 flow directions
mpiexec -n 224 d8flowdir -p $out/demp.tif -sd8 $out/demsd8.tif -fel $out/demfel.tif

# # # Contributing area
mpiexec -n 224 aread8 -p $out/demp.tif -ad8 $out/demad8.tif
# #mpiexec -n 224 aread8 -p demp.tif -ad8 demad8.tif -o out1.shp -nc 

# # # Grid Network 
mpiexec -n 224 gridnet -p $out/demp.tif -gord $out/demgord.tif -plen $out/demplen.tif -tlen $out/demtlen.tif

# # Threshold equals to 96 acres
mpiexec -n 224 threshold -ssa $out/demad8.tif -src $out/demsrc.tif -thresh $npixels

# #streamnet
#mpiexec -n 224 streamnet -fel demfel.tif -p demp.tif -ad8 demad8.tif -src demsrc.tif -ord demord.tif -tree demtree.txt -coord demcoord.txt -net demnet.shp -w demw.tif


