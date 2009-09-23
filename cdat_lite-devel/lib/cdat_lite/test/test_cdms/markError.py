#!/usr/bin/env python
# Adapted for numpy/ma/cdms2 by convertcdms.py

import numpy.ma as MA

from pkg_resources import resource_filename

errors = []

NTIME = 3
NLAT = 16
NLON = 32

x = MA.arange(float(2*NTIME*NLAT*NLON))
x.shape=(2,NTIME,NLAT,NLON)

# Make exceptions compatible with unittest
from unittest import TestCase
class CdTestException(TestCase.failureException):
    pass

def clearError():
    global errors
    errors = []

def markError(error,val=None):
    global errors
    if val is not None: error = error+': '+`val`
    errors.append(error)

def reportError():
    if errors==[]:
        print 'OK'
    else:
        print 'Failed'
        raise CdTestException,errors

def get_sample_data_dir():
    """
    Wrapper to replace references to sys.prefix in the test scripts.

    """
    
    return resource_filename('cdat_lite.test.test_cdms', 'sample_data')
