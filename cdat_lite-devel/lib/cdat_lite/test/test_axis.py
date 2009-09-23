# Adapted for numpy/ma/cdms2 by convertcdms.py
"""
Test axis features of CDMS.

@note: These tests expect to be invoked using nose.

"""

import tempfile, os
import cdms2 as cdms, numpy.oldnumeric.ma as MA
import numpy.oldnumeric as N

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
