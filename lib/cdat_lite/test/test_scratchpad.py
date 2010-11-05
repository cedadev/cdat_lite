# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
An informal module for noting down things that might need testing.

"""

import pkg_resources, cdms2
import numpy

def test_netcdf():
    """
    Some problems being encountered using cdms on Python2.5

    """

    f = pkg_resources.resource_filename('cdat_lite.test', 'tas_mo_clim.nc')
    d = cdms2.open(f)
    v = d['climseas']
    s = v[slice(0,1,None)]
    assert s.shape == (1,45,72)


def test_slice():
    """
    Problems with slicing on x86_64.

    """
    a = numpy.array([0])
    var = cdms2.createVariable(a)
    # This fails
    print var[:]
    
