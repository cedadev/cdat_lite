# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
Test axis features of CDMS.

@note: These tests expect to be invoked using nose.

"""

import tempfile, os
import cdms2 as cdms, numpy.ma as MA
import numpy as N

def test_createAxis():
    # On 64-bit systems this test fails due to attempted long to int
    # type conversion inside cdms

    # Also fails with cdms2 on 64-bit.

    # Create a temporary file
    fd, f = tempfile.mkstemp('.nc')
    os.close(fd)
    try:
        # Create an axis in a temporary NetCDF file
        d = cdms.open(f, 'w')
        ax_d = N.arange(10)
        try:
            ax = d.createAxis('x', ax_d)
        except TypeError, e:
            print e
            raise AssertionError
        assert isinstance(ax, cdms.axis.FileAxis)
    finally:
        d.close()
        os.remove(f)
        
def test_castAxis():
    # This fails with Numeric-24.2
    # the same bug is exposed by one of the cdtest modules
    # This is because cdms objects don't implement the array interface.

    # Also fails with cdms2 on 64-bit.  Maybe this shouldn't be expected to work.

    ax = cdms.createAxis([1,2,3,4])
    n = N.array(ax)

    print 'n.shape = %s' % (n.shape,)
    print 'ax.shape = %s' % (ax.shape,)
    
    assert n.shape == ax.shape


def test_axis_segfault():
    from cdms2 import MV2

    # Contributed by Lawson Hanson
    month = 'January'
    year  = '2012'
    miss_value = -9999.0

    data = ['34.006348', '28.314002', '29.269668', '33.698551', '34.177242']

    Rad_global_month = MV2.zeros([len(data)],MV2.float)
    time_day = MV2.zeros([len(data)],MV2.float)
    tim = cdms.createAxis(time_day)
    tim.designateTime()
    tim.id = "time"
    tim.units = 'days since 2012-01-01'

    for i in range(len(time_day)):
        Rad_global_month[i] = data[i]
        tim[i] = float(i)
        
    # Create a temporary file
    fd, f = tempfile.mkstemp('.nc')
    os.close(fd)
    try:
        out = cdms.open(f,'w')
            
        rad_total_month = cdms.createVariable(Rad_global_month,id = 'accum_swfcdown_'+month,axis=[tim],typecode='f')
        rad_total_month.setAxisList([tim]) 

        print rad_total_month,tim
        print len(rad_total_month),len(tim)

        out.write(rad_total_month)
    finally:
        out.close()
        os.remove(f)
