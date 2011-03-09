"""
Test reading of scalar NetCDF variables.

These tests verify whether a scalar NetCDF variable behaves like a
Numpy zero-rank array according to the documentation at 
http://projects.scipy.org/numpy/wiki/ZeroRankArray

"""

import os, sys

import cdms2
import numpy

zero_rank_fn = os.path.join(os.path.dirname(__file__), 'zero_rank.nc')
zero_rank = cdms2.open(zero_rank_fn)
z = zero_rank['height']

def test_shape():
    assert z.shape == ()

def test_ellipsis():
    v = z[...]

    assert type(v) == type(z)

def test_tuple():
    v = z[()]

    assert type(v) == numpy.float64

def test_item():
    #!WARNING: may fail on 32-bit systems
    v = z.item()

    assert type(v) == float
