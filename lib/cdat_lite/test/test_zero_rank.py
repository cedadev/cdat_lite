"""
Test reading of scalar NetCDF variables.

These tests verify whether a scalar NetCDF variable behaves like a
Numpy zero-rank array according to the documentation at 
http://projects.scipy.org/numpy/wiki/ZeroRankArray

"""

import os, sys

import cdms2
import numpy


# Switching on NumericCompatibility changes the result.
#cdms2.setNumericCompatibility(True)

zero_rank_fn = os.path.join(os.path.dirname(__file__), 'zero_rank.nc')
zero_rank = cdms2.open(zero_rank_fn)
z = zero_rank['height']

def test_shape():
    # Sanity check
    assert z.shape == ()

def test_ellipsis():
    v = z[...]

    # By analogy of what we get for non-scalar variables
    print v, type(v)
    assert type(v) == cdms2.tvariable.TransientVariable

def test_tuple():
    v = z[()]

    print v, type(v)
    assert type(v) == numpy.float64

def test_item():
    #!WARNING: may fail on 32-bit systems
    v = z.item()

    print v, type(v)
    assert type(v) == float
