"""Module cdutil contains miscellaneous routines for manipulating variables.
"""
import region
# Don't import this by default because it uses vcs
#import continent_fill
from genutil.averager import averager, AveragerError, area_weights, getAxisWeight, getAxisWeightByName,__check_weightoptions
from times import *
from retrieve import WeightsMaker,  WeightedGridMaker, VariableConditioner, VariablesMatcher
from vertical import sigma2Pressure, reconstructPressureFromHybrid, logLinearInterpolation, linearInterpolation