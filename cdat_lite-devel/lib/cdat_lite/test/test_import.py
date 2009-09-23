#!/usr/bin/env python
"""
Test importing sub-packages.

@author: Stephen Pascoe
"""

import unittest

class ImportTests(unittest.TestCase):

    def tryImport(self, moduleName):
        try:
            exec ("import %s" % moduleName) in globals()
        except:
            raise self.failureException

    def testCdms(self): self.tryImport('cdms2')
    def testCdtime(self): self.tryImport('cdtime')
    def testCdutil(self): self.tryImport('cdutil')
    def testGenutil(self): self.tryImport('genutil')
    def testRegrid(self): self.tryImport('regrid2')


def test_numeric():
    """Test the version of Numeric being used
    """
    import Numeric
    print 'Python-23.1 is required for reliable cdat_lite behaviour'
    assert Numeric.__version__.split('.')[0] == '23'
