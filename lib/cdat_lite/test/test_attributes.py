# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
This test exposes a bug in 64-bit Numeric.  Attributes are reported
as arrays of arrays of scalars.

"""

import pkg_resources, cdms2 as cdms, sys
import numpy as N
import numpy

def test_attributeType():
    fn = pkg_resources.resource_filename('cdat_lite.test', 'testpp.pp')
    f = cdms.open(fn)
    assert f.input_word_length == [4,]
    assert type(f.input_word_length) == type(N.zeros(1))

    # numpy returns special scalar types.  This test should pass now.
    assert f.input_word_length.dtype == numpy.dtype('int32')

