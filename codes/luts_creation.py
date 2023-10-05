import numpy as np 
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