"""
This test exposes a bug in 64-bit Numeric.  Attributes are reported
as arrays of arrays of scalars.

This test is deactivated for now because I've worked around the problem in cdscan.

"""

import pkg_resources, cdms, sys
import Numeric

def test_attributeType():
    fn = pkg_resources.resource_filename('cdat_lite.test', 'testpp.pp')
    f = cdms.open(fn)
    assert f.input_word_length == [4,]
    assert type(f.input_word_length) == type(Numeric.zeros(1))
    assert type(f.input_word_length[0]) == type(1)

def test_arange():
    a = Numeric.arange(10)
    assert list(a[1:]) == [1,2,3,4,5,6,7,8,9]
