"""
Create a variable in a file.
"""


import os
from unittest import TestCase
import tempfile

import numpy
import cdms2

cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)

class TestMakevar(TestCase):

    def do(self, dtype):
        fd, tmp = tempfile.mkstemp(suffix='.nc')
        os.close(fd)
        
        print 'Creating temporary NetCDF file %s' % tmp
        self.make_var(tmp, dtype)


    def make_var(self, fn, dtype):
        var = cdms2.createVariable(numpy.array([0], dtype=dtype))

        f = cdms2.open(fn, 'w')
        f.write(var, id='test')
        f.close()

    def test_default(self):
        self.do(None)

    def test_int32(self):
        self.do(numpy.int32)

    def fulltest_int64(self):
        self.do(numpy.int64)

    def test_float32(self):
        self.do(numpy.float32)

    def test_float64(self):
        self.do(numpy.float64)



class TestMakeGridVar(TestCase):

    def make_gridvar(self, a, g):
        return cdms2.createVariable(a, grid=g)

    def make_axesvar(self, a, g):
        return cdms2.createVariable(a, 
                                    axes=[g.getLatitude(),
                                          g.getLongitude()])

    def make_axeswithtime(self, a, g, t):
        return cdms2.createVariable(numpy.array([a]),
                                    axes=[t, g.getLatitude(),
                                          g.getLongitude()])

    def make_array(self, grid):
        lat = grid.getLatitude().getValue(); nlat = len(lat)
        lon = grid.getLongitude().getValue(); nlon = len(lon)

        lat_m = numpy.ones((nlat, nlon)) * numpy.reshape(lat, (nlat, 1))
        lon_m = numpy.ones((nlat, nlon)) * lon

        return lat_m + lon_m

    def make_time(self):
        t = cdms2.createAxis(numpy.array([0]))
        t.id = 'time'
        t.units = 'days since 2000-01-01'
        t.designateTime()

        return t

    def save(self, var):
        fd, tmp = tempfile.mkstemp(suffix='.nc')
        os.close(fd)
        
        print 'Creating temporary NetCDF file %s' % tmp
        f = cdms2.open(tmp, 'w')
        f.write(var, id='test')
        f.close()

    def make_grid(self):
        return cdms2.createUniformGrid(-87.5, 36, 5.0, 5, 36, 10)

    def test_grid(self):
        g = self.make_grid()
        a = self.make_array(g)
        var = self.make_gridvar(a, g)
        self.save(var)

    def test_axes(self):
        g = self.make_grid()
        a = self.make_array(g)
        var = self.make_axesvar(a, g)
        self.save(var)

    def fulltest_axeswithtime(self):
        g = self.make_grid()
        a = self.make_array(g)
        t = self.make_time()
        var = self.make_axeswithtime(a, g, t)
        self.save(var)

