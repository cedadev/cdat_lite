"""
Tests to check you can open files for writing in different circumstances.

"""

import tempfile, os
import cdms2 as cdms, numpy.ma as MA
import numpy as N
import shutil
import os.path as op

TEST_DIR = op.dirname(__file__)
SMALL_NC = op.join(TEST_DIR, 'foo.nc')

def test_overwrite_file():
    # Create a temporary file
    fd, f = tempfile.mkstemp('.nc')
    os.close(fd)

    # the file exists and is empty
    d = cdms.open(f, 'w')

    # Set a global attribute and close
    d.foo_attribute = 'bar'
    d.close()

    d = cdms.open(f)
    assert d.foo_attribute == 'bar'

def test_overwrite_file2():
    fd, f = tempfile.mkstemp('.nc')
    os.close(fd)
    shutil.copy(SMALL_NC, f)

    d = cdms.open(f, 'w')

    # Set a global attribute and close
    d.foo_attribute = 'bar'
    d.close()

    d = cdms.open(f)
    assert d.foo_attribute == 'bar'


