import gdal 
import osgeo

def read_raster(path_map,isDEMorDIR=False,dxp=None, noDataP = None,isDIR = False,DIRformat = 'r.watershed'):
    'Funcion: read_map\n'\
    'Descripcion: Lee un mapa raster soportado por GDAL.\n'\
    'Parametros Obligatorios:.\n'\
    '   -path_map: path donde se encuentra el mapa.\n'\
    'Parametros Opcionales:.\n'\
    '   -isDEMorDIR: Pasa las propiedades de los mapas al modulo cuencas \n'\
    '       escrito en fortran \n'\
    '   -dxp: tamano plano del mapa\n'\
    '   -noDataP: Valor para datos nulos en el mapa (-9999)\n'\
    '   -DIRformat: donde se ha conseguido el mapa dir (r.watershed) \n'\
    '       - r.watershed: mapa de direcciones obtenido por la funcion de GRASS\n'\
    '       - opentopo: mapa de direcciones de http://www.opentopography.org/\n'\
    '   -isDIR: (FALSE) es este un mapa de direcciones\n'\
    'Retorno:.\n'\
    '   Si no es DEM o DIR retorna todas las propieades del elemento en un vector.\n'\
    '       En el siguiente orden: ncols,nrows,xll,yll,dx,nodata.\n'\
    '   Si es DEM o DIR le pasa las propieades a cuencas para el posterior trazado.\n'\
    '       de cuencas y link_ids.\n' \
    #Abre el mapa
    direction=gdal.Open(path_map)
    #Projection
    proj = osgeo.osr.SpatialReference(wkt=direction.GetProjection())
    EPSG_code = proj.GetAttrValue('AUTHORITY',1)
    #lee la informacion del mapa
    ncols=direction.RasterXSize
    nrows=direction.RasterYSize
    banda=direction.GetRasterBand(1)
    noData=banda.GetNoDataValue()
    geoT=direction.GetGeoTransform()
    dx=geoT[1]
    dy=geoT[-1]
    xll=geoT[0]; yll=geoT[3]
    #lee el mapa
    Mapa=direction.ReadAsArray()
    direction.FlushCache()
    del direction
    return Mapa.astype(float),[ncols,nrows,xll,yll,dx,dy,noData],EPSG_code


def get_slice_location(po,ps):
    '''uses the prop of the origin and slice to obtain the 
    Columns before and after, Cb and Ca, respectively and 
    the Number of rows before (Rb)'''
    # Deine the X and y's 
    x1 = ps[2]
    y1 = ps[3]#+ps[5]*ps[1]
    Nc1 = ps[0]
    Nr1 = ps[1]

    x2 = po[2]
    y2 = po[3]#+po[5]*po[1]
    Nc2 = po[0]
    Nr2 = po[1]

    dx = po[4]
    dy = po[5]
    
    Cb = int(np.ceil((x1-x2)/dx))
    Ca = int(Cb + Nc1)
    Rb = int(np.ceil((y1 - y2) / dy))
    return Cb, Ca, Rb, Nr1

def save_array2raster(Array, ArrayProp, path, EPSG = 4326, Format = 'GTiff', dtype = 'int32', proj4 = None):
    dst_filename = path
    #Change the array format to int32 
    Array = Array.astype(dtype)
    #Formato de condiciones del mapa
    x_pixels = Array.shape[1]  # number of pixels in x
    y_pixels = Array.shape[0]  # number of pixels in y
    PIXEL_SIZE_x = ArrayProp[4]  # size of the pixel... 
    PIXEL_SIZE_y = ArrayProp[5]  # size of the pixel...
    x_min = ArrayProp[2]
    y_max = ArrayProp[3] #+ ArrayProp[5] * ArrayProp[1] # x_min & y_max are like the "top left" corner.
    driver = gdal.GetDriverByName(Format)
    #Para encontrar el formato de GDAL
    NP2GDAL_CONVERSION = {
      "uint8": 1,
      "int8": 1,
      "uint16": 2,
      "int16": 3,
      "uint32": 4,
      "int32": 5,
      "float32": 6,
      "float64": 7,
      "complex64": 10,
      "complex128": 11,
    }
    gdaltype = NP2GDAL_CONVERSION[Array.dtype.name]
    # Crea el driver
    dataset = driver.Create(
        dst_filename,
        x_pixels,
        y_pixels,
        1,
        gdaltype,)
    #coloca la referencia espacial
    dataset.SetGeoTransform((
        x_min,    # 0
        PIXEL_SIZE_x,  # 1
        0,                      # 2
        y_max,    # 3
        0,                      # 4
        PIXEL_SIZE_y))
    #coloca la proyeccion a partir de un EPSG
    proj = osgeo.osr.SpatialReference()
    if proj4 == None:
        texto = 'EPSG:' + str(EPSG)
        proj.SetWellKnownGeogCS( texto )
    else:
        proj.SetProjection(proj4)
    dataset.SetProjection(proj.ExportToWkt())
    #Coloca el nodata
    band = dataset.GetRasterBand(1)
    if ArrayProp[-1] is None:
        band.SetNoDataValue(-9999)
    else:
        band.SetNoDataValue(int(ArrayProp[-1]))
    #Guarda el mapa
    dataset.GetRasterBand(1).WriteArray(Array)
    dataset.FlushCache()