"""
Tests exposing missing CmdsFile.dimensions attribute.

"""

import os

import cdms2

ncfile = os.path.join(os.path.dirname(__file__), 'tas_mo_clim.nc')

def test_dimension_isUnlimeted():
    f = cdms2.open(ncfile)
    try:
        v = f.variables['climseas']
        t = v.getTime()

        # fails with AttributeError: CdmsFile.dimensions
        assert t.isUnlimited()
    finally:
        f.close()

def test_dimensions_attr():
    f = cdms2.open(ncfile)
    try:
        # Fails with AttributeError
        print f.dimensions.keys()
    finally:
        f.close()
#
# CdmsFile.dimensions now assumed to be not part of the API.
#
test_dimensions_attr.__test__ = False    
