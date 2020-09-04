'''
Backport from django 1.10
'''

import math

from ctypes import byref, c_double, c_int, c_void_p, POINTER

from django.contrib.gis.gdal.libgdal import std_call
from django.contrib.gis.gdal.prototypes.generation import void_output

get_band_statistics = void_output(std_call('GDALGetRasterStatistics'),
    [
        c_void_p, c_int, c_int, POINTER(c_double), POINTER(c_double),
        POINTER(c_double), POINTER(c_double), c_void_p, c_void_p,
    ],
    errcheck=False
)
compute_band_statistics = void_output(std_call('GDALComputeRasterStatistics'),
    [c_void_p, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), c_void_p, c_void_p],
    errcheck=False
)

def band_statistics(band, refresh=False, approximate=False):
    """
    Compute statistics on the pixel values of this band.
    The return value is a tuple with the following structure:
    (minimum, maximum, mean, standard deviation).
    If approximate=True, the statistics may be computed based on overviews
    or a subset of image tiles.
    If refresh=True, the statistics will be computed from the data directly,
    and the cache will be updated where applicable.
    For empty bands (where all pixel values are nodata), all statistics
    values are returned as None.
    For raster formats using Persistent Auxiliary Metadata (PAM) services,
    the statistics might be cached in an auxiliary file.
    """
    # Prepare array with arguments for capi function
    smin, smax, smean, sstd = c_double(), c_double(), c_double(), c_double()
    stats_args = [
        band._ptr, c_int(approximate), byref(smin), byref(smax),
        byref(smean), byref(sstd), c_void_p(), c_void_p(),
    ]

    if refresh:
        compute_band_statistics(*stats_args)
    else:
        # Add additional argument to force computation if there is no
        # existing PAM file to take the values from.
        force = True
        stats_args.insert(2, c_int(force))
        get_band_statistics(*stats_args)

    result = smin.value, smax.value, smean.value, sstd.value

    # Check if band is empty (in that case, set all statistics to None)
    if any((math.isnan(val) for val in result)):
        result = (None, None, None, None)

    band._stats_refresh = False

    return result
