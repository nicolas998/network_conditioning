# Iowa HD Processing for IFIS

This repository contains the steps followed to generate the network and hillslopes used for IFIS to run the operational HLM model. 
The generation of the data relies on USGS 1/3 arc (~10m) Digital Elevation Models (DEM) obtained from https://apps.nationalmap.gov/
and the NHDPlus High definition network obtained form (XXXX). After the generation of the network, the process also includes the conflation between 
the network and the NHDPlus network, and the generation of the tiles for the web.
In the process, we used the following software and python packages:

- TauDEM
- GDAL
- geopandas 
- numpy 

# Steps 
---
## Process DEM burning NHDPlus 

In this step we burned the NHDPlus High definition network into the DEM and the processed it using TauDEM
the burning process involved using the upstream area to determine the depth. The computation of this procedure 
can be found in the folder:

- [x] codes/nhd_depth2burn.py 

Examples and plots of the procedure can be found at 

- [x] notebooks/nhd_depth2burn.ipynb

### Processing the dem with TauDEM

After running *nhd_depth2butn.py* the map can be used to burn the DEM and process it in TauDEM using the code at:

- [x] codes/proces_dem.sh

Process_dem.sh will produce **demnet.shp** and **hills.shp** at the *Dedicated* folder. Both are analyzed in 

- [x] notebooks/test_hills_streams.ipynb

### Remove virtual links from the network

TauDem generates some virtual links to keep a binary treep structure. we remove those links form the *network.shp* using the following code 

- [ ] codes/remove_virtual_links.py
- [ ] notebooks/remove_virtual_links.ipynb

---
## Extract HLM required files and test HLM

### Extract rvr, prm, luts

After processing the net, we extracted the **rvr** and **prm** files required for HLM. This step also includes the extraction of the lookup tables **"lut"** that 
relates forcings grids to the hillslopes. The rvr and prm are obtained through the following codes:

- [ ] codes/net2rvr.py 
- [ ] codes/net2prm.py 

The **lut** files are processed using the following codes:

- [ ] codes/get_luts.py

### Testing HLM

After generating the required files, we test HLM using the new network, the files for the test can be found at:
- hlm_files/

The codes to set up the required files such as globals (**gbl**) and run files are at:
- [ ] codes/hlm_gen_global.py
- [ ] codes/hlm_gen_run.py
- [ ] codes/hlm_process_dats.py

---
## Tiles generation 

After testing HLM, we create the tiles for the web, a copy of the code can be found at 
- [ ] codes/tiles_gen.py
- [ ] codes/tiles_main.py 

Nevertheless, due to the amount of data, we generate the tiles in the server that will contain them. 

---
## Network conflation to NHDPlus

In this step we asing the NHDPlus COMID to the LINKNO of the network.shp. This assignation allows to have the names of the rivers in the network 
and also to perform comparison between NWC and the IFC forecasts. The code for the conflation can be found at:

- [ ] codes/net2nhd.py

