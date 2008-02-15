# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
Tests on rotated grids.

"""

from unittest import TestCase
import pkg_resources
import cdms2 as cdms

# These two files are identical except one defines it's true longitude in
# the domain -180 to 180 and the other 0 to 360.
rotgrid180 = pkg_resources.resource_filename('cdat_lite.test', 'rg180.nc')
rotgrid360 = pkg_resources.resource_filename('cdat_lite.test', 'rg360.nc')

class TestRotGrid(TestCase):
    def _doSubset(self, cdms_file):
        return cdms_file('temp_1', lon=(-7,2), lat=(50,55))

    def _printSubset(self, v):
        print 'Shape of v = ', v.shape
        for ax in v.getAxisList():
            print ax.id, list(ax.getValue())
    
    def test180(self):
        f = cdms.open(rotgrid180)
        v = self._doSubset(f)
        self._printSubset(v)
        assert v[15,15].mask == False
        assert v[15,15] > 270.

    def test360(self):
        f = cdms.open(rotgrid360)
        v = self._doSubset(f)
        self._printSubset(v)
        assert v[15,15].mask == False
        assert v[15,15] > 270.
