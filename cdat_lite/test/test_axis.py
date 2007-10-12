"""
Test axis features of CDMS.

@note: These tests expect to be invoked using nose.

"""

import tempfile, os
import cdms
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
        ax = d.createAxis('x', ax_d)
        assert isinstance(ax, cdms.axis.FileAxis)
    finally:
        d.close()
        os.remove(f)
        

def test_intTypecode():
    # This is the underlying bug exposed by test_createAxis.
    # Numeric-24.2 can cast typecodes 'l' to 'i' on 32-bit systems but
    # not 64-bit systems.  Basically I think the move to 64-bit screws up the
    # typecode character identifiers.
    # Work-arround: Use Numeric-23.1 as PCMDI are doing.
    
    x = N.zeros((10,), typecode='i')
    y = N.ones((10,), typecode='l')

    # Raises exception on 64-bit
    x[1:3] = y[1:3]

    # Check the array is right
    assert list(x) == [0,1,1,0,0,0,0,0,0,0]
