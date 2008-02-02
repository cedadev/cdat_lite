"""
Test axis features of CDMS.

@note: These tests expect to be invoked using nose.

"""

import tempfile, os
import cdms, MA
import Numeric as N

def test_createAxis():
    # On 64-bit systems this test fails due to attempted long to int
    # type conversion inside cdms

    # Create a temporary file
    fd, f = tempfile.mkstemp('.nc')
    os.close(fd)
    try:
        # Create an axis in a temporary NetCDF file
        d = cdms.open(f, 'w')
        ax_d = N.arange(10)
        try:
            ax = d.createAxis('x', ax_d)
        except TypeError:
            raise AssertionError
        assert isinstance(ax, cdms.axis.FileAxis)
    finally:
        d.close()
        os.remove(f)
        
def test_maskAxis():
    # This fails with Numeric-24.2
    # the same bug is exposed by one of the cdtest modules

    ax = cdms.createAxis([1,2,3,4])
    m = MA.masked_array(ax)
    assert m.shape == (4,)
