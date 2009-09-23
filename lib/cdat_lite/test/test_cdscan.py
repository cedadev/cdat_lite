"""
Test cdscan.

"""

from unittest import TestCase
import pkg_resources
import os

from cdat_lite.scripts import cdscan
import tempfile

class TestCdscan(TestCase):
    """
    Cdscanning pp files on 64-bit linux was crashing because of a bug in Numeric.
    This has been circumvented in cdms.cdmsNode.  Here we test that it's working.

    """
    f = pkg_resources.resource_filename('cdat_lite.test', 'testpp.pp')

    def testPP(self):
        (fd, t) = tempfile.mkstemp(); os.close(fd)

        try:
            cdscan.main(['cdscan', '-x', t, self.f])
        finally:
            os.remove(t)
            
