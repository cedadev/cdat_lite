#!/usr/bin/env python
# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
Test reading data with cdms.

@author: Stephen Pascoe
"""

import unittest, pkg_resources, cdms2 as cdms, sys

class CdmsTests(unittest.TestCase):

    def testNetCDF(self):
        f = pkg_resources.resource_filename('cdat_lite.test', 'tas_mo_clim.nc')
        d = cdms.open(f)
        vars = d.listvariables()
        vars.sort()
        self.assert_(vars == ['bounds_latitude', 'bounds_longitude', 'climseas'])

    def testPP(self):
        f = pkg_resources.resource_filename('cdat_lite.test', 'testpp.pp')
        d = cdms.open(f)
        vars = d.listvariables()
        vars.sort()
        self.assert_(vars == ['p0', 'ps', 'time_bnd0', 'u',
                              'z1_hybrid_sigmap_acoeff', 'z1_hybrid_sigmap_bcoeff'])
