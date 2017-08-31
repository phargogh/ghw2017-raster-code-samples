import os
from osgeo import gdal
import numpy

_SCENE_ID = 'LC08_L1TP_042034_20130605_20170310_01_T1'
_LANDSAT_DIR = os.path.join(os.path.expanduser('~'),
                            'Downloads', 'geohackweek2017', _SCENE_ID)
L8_RED = os.path.join(_LANDSAT_DIR, _SCENE_ID + '_B4.TIF')
L8_NIR = os.path.join(_LANDSAT_DIR, _SCENE_ID + '_B5.TIF')


def ndvi(red, nir):
    """Calculate NDVI from the two bands."""
    return (nir - red) / (nir + red)


def ndvi_gdal():
    """Use GDAL to calculate NDVI."""
    red_dataset = gdal.Open(L8_RED)
    red_matrix = red_dataset.ReadAsArray()

    nir_dataset = gdal.Open(L8_NIR)
    nir_matrix = nir_dataset.ReadAsArray()

    gtiff_driver = gdal.GetDriverByName('GTiff')
    new_dataset = gtiff_driver.Create(
        'ndvi.tif', red_dataset.RasterXSize, red_dataset.RasterYSize, 1,
        gdal.GDT_Float32)
    new_dataset.SetProjection(red_dataset.GetProjection())
    new_dataset.SetGeoTransform(red_dataset.GetGeoTransform())

    new_band = new_dataset.GetRasterBand(1)

    new_band.WriteArray(ndvi(
        red_matrix.astype(numpy.float32), nir_matrix.astype(numpy.float32)))
    new_band = None
    new_dataset = None


if __name__ == '__main__':
    ndvi_gdal()






