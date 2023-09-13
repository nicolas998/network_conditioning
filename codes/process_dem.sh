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
dem=/Dedicated/IFC/Nicolas/iowa_hd/with_nhd_high/dem_cut.tif
nhd=/Users/nicolas/2023_iowa_hd/maps/merged_BurnLines_20230912.shp
out=/Dedicated/IFC/Nicolas/iowa_hd/with_nhd_high

#Merge dems
#gdal_merge.py -ot Float32 -of GTiff -o $out/dem_merged.tif --optfile $out/files2merge.txt

#Project merged dem
#gdalwarp -s_srs EPSG:4269 -t_srs EPSG:26915 -tr 10.0 10.0 -r near -of GTiff $out/dem_merged.tif $out/dem_proj.tif

#Crop dem to the area of interest 
#gdalwarp -of GTiff -cutline $out/buffer_simple.shp -cl buffer_simple -crop_to_cutline $out/dem_proj.tif $out/dem_cut.tif

#Rasterizes the network
gdal_calc.py --calc=A*0 --outfile=$out/network.tif -A $dem --overwrite
gdal_rasterize -a depth $nhd $out/network.tif # variable case 
#gdal_rasterize -burn 1 $nhd $out/network.tif # constant case
#gdal_rasterize -add -burn -30 -l $dem $nhd $out/network.tif #Method that didin't worked

# # # #Burns the network into the DEM
gdal_calc.py --calc=A-B --outfile=$out/dem_burn.tif -A $dem -B $out/network.tif --overwrite 
#gdal_calc.py --calc=A-B*30 --outfile=$out/dem_burn.tif -A $dem -B $out/network.tif --overwrite 

# # # Pitremove
mpiexec -n 224 pitremove -z $out/dem_burn.tif -fel $out/demfel.tif

# # # D8 flow directions
mpiexec -n 224 d8flowdir -p $out/demp.tif -sd8 $out/demsd8.tif -fel $out/demfel.tif

# # # # Contributing area
mpiexec -n 224 aread8 -p $out/demp.tif -ad8 $out/demad8.tif
# # #mpiexec -n 224 aread8 -p demp.tif -ad8 demad8.tif -o out1.shp -nc 

# # # # Grid Network 
mpiexec -n 224 gridnet -p $out/demp.tif -gord $out/demgord.tif -plen $out/demplen.tif -tlen $out/demtlen.tif

# # # Threshold equals to 96 acres
mpiexec -n 224 threshold -ssa $out/demad8.tif -src $out/demsrc.tif -thresh $npixels

#streamnet
mpiexec -n 224 streamnet -fel $out/demfel.tif -p $out/demp.tif -ad8 $out/demad8.tif -src $out/demsrc.tif -ord $out/demord.tif -tree $out/demtree.txt -coord $out/demcoord.txt -net $out/demnet.shp -w $out/demw.tif

#convert watersheds to shp 
gdal_polygonize.py $out/demw.tif -b 1 -f "ESRI Shapefile" $out/hills.shp hills LINKNO 

