"""Module cdutil contains miscellaneous routines for manipulating variables.
"""
import region
try:
    import continent_fill
except ImportError:
    pass
from genutil.averager import averager, AveragerError, area_weights, getAxisWeight, getAxisWeightByName,__check_weightoptions
from times import *
from retrieve import WeightsMaker,  WeightedGridMaker, VariableConditioner, VariablesMatcher
from vertical import sigma2Pressure, reconstructPressureFromHybrid, logLinearInterpolation, linearInterpolation
from create_landsea_mask import generateLandSeaMask
from sftbyrgn import generateSurfaceTypeByRegionMask
