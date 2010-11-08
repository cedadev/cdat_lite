# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
An informal module for noting down things that might need testing.

"""

import pkg_resources, cdms2
import numpy, os

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
    I've narrowed this down to a numpy.ma problem.
    This works on numpy-1.5 but not numpy-1.4.1

    """
    import numpy.ma
    a = numpy.ma.array([0])
    # This fails with numpy-1.4.1
    print a[:]
    
def test_makevar():
    """
    Regression test for changes to the numpy.ma._fill_value implementation.

    """
    a = numpy.array([0])
    var = cdms2.createVariable(a)
    tmp = '/tmp/test_makevar.nc'
    try:
        f = cdms2.open(tmp, 'w')
        f.write(var, id='test')
        f.close()
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_modulo():
    """
    A problem with modulo of CDMS variables has been reported with
    numpy-1.5.0

    """
    a = numpy.arange(10)
    var = cdms2.createVariable(a)
    # Fails here
    m = var % 2

    assert m.tolist() == [0,1,0,1,0,1,0,1,0,1]

def test_arithmathic():
    """
    As contributed by Chris (lee@ashimaresearch.com)

    """
    nc_file = pkg_resources.resource_filename('cdat_lite.test', 'lee_data.nc')
    nc = cdms2.open(nc_file)
    d = nc.variables["data"]

    statements = ["d2 =  d + 10.",
                  "d2 =  d / 10.",
                  "d2 =  d % 10.",
                  "d2 =  d[:] + 10.",
                  "d2 =  d[:] / 10.",
                  "d2 =  d[:] % 10.",
                  "d2 =  d[:].data + 10.",
                  "d2 =  d[:].data / 10.",
                  "d2 =  d[:].data % 10.",
                  ]

    fail = False
    for s in statements:
        try:
            exec(s)
            print("success: {0}".format(s))
        except:
            fail = True
            print("fail   : {0}".format(s))

    if fail:
        raise AssertionError("Arithmatic test failure")
