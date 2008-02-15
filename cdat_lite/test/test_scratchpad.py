# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
An informal module for noting down things that might need testing.

"""

import pkg_resources, cdms2 as cdms

def test_netcdf():
    """
    Some problems being encountered using cdms on Python2.5

    """

    f = pkg_resources.resource_filename('cdat_lite.test', 'tas_mo_clim.nc')
    d = cdms.open(f)
    v = d['climseas']
    s = v[slice(0,1,None)]
    assert s.shape == (1,45,72)

