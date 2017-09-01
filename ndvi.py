import os
from osgeo import gdal
import numpy
import rasterio
import rasterio.dtypes
import pygeoprocessing

_SCENE_ID = 'LC08_L1TP_042034_20130605_20170310_01_T1'
_LANDSAT_DIR = os.path.join(os.path.expanduser('~'),
                            'Downloads', 'geohackweek2017', _SCENE_ID)
L8_RED = os.path.join(_LANDSAT_DIR, _SCENE_ID + '_B4.TIF')
L8_NIR = os.path.join(_LANDSAT_DIR, _SCENE_ID + '_B5.TIF')


def ndvi(red, nir):
    """Calculate NDVI from the two bands."""
    red = red.astype(numpy.float)
    nir = nir.astype(numpy.float)
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

    new_band.WriteArray(ndvi(red_matrix, nir_matrix))
    new_band.ComputeStatistics(False)  # apprimations not permitted
    new_band = None
    new_dataset = None


def ndvi_rasterio():
    with rasterio.open(L8_RED) as red_raster:
        red_matrix = red_raster.read(1)
        source_crs = red_raster.crs
        source_transform = red_raster.transform

    with rasterio.open(L8_NIR) as nir_raster:
        nir_matrix = nir_raster.read(1)

    calculated_ndvi = ndvi(red_matrix, nir_matrix)

    with rasterio.open('ndvi_rasterio.tif', 'w', driver='GTiff',
                       height=red_matrix.shape[0],
                       width=red_matrix.shape[1],
                       count=1, dtype=rasterio.dtypes.float64,
                       crs=source_crs,
                       transform=source_transform) as out_raster:
        out_raster.write(calculated_ndvi, 1)


def ndvi_pygeoprocessing():
    red_raster_info = pygeoprocessing.get_raster_info(L8_RED)
    pygeoprocessing.raster_calculator(
        [(L8_RED, 1), (L8_NIR, 1)], ndvi,
        'ndvi_pygeoprocessing.tif', gdal.GDT_Float32,
        red_raster_info['nodata'][0], calc_raster_stats=True)


if __name__ == '__main__':
    ndvi_gdal()
    ndvi_rasterio()
    ndvi_pygeoprocessing()
