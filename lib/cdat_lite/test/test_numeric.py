# Adapted for numpy/ma/cdms2 by convertcdms.py
import numpy as N
from nose.tools import *

def test_arange():
    # On 64-bit linux this fails with both Numeric-24.2 and Numeric-23.1
    # but in different ways.

    a = N.arange(10)
    assert list(a[1:]) == [1,2,3,4,5,6,7,8,9]


def test_intTypecode():
    # This is the underlying bug exposed by test_axis.test_createAxis.
    # Numeric-24.2 can cast typecodes 'l' to 'i' on 32-bit systems but
    # not 64-bit systems.  Basically I think the move to 64-bit screws up the
    # typecode character identifiers.
    # Work-arround: Use Numeric-23.1 as PCMDI are doing.
    
    x = N.zeros((10,), dtype='i')
    y = N.ones((10,), dtype='l')

    # Raises exception on 64-bit
    try:
        x[1:3] = y[1:3]
    except TypeError:
        raise AssertionError
    # Check the array is right
    assert list(x) == [0,1,1,0,0,0,0,0,0,0]

def test_booleans():
    # numpy doesn't let you do boolean tests on arrays.  Use a.all() instead
    a = N.ones(5)

    assert_raises(ValueError, lambda: not a)

    assert_true(a.all())
