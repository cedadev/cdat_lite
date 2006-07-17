#!/usr/bin/env python
"""
Test suite for CDAT mini-install

@author: Stephen pascoe
"""

import unittest

class ImportTests(unittest.TestCase):

    def tryImport(self, moduleName):
        try:
            exec ("import %s" % moduleName) in globals()
        except:
            raise self.failureException

    def testCdms(self): self.tryImport('cdms')
    def testCdtime(self): self.tryImport('cdtime')
    def testCdutil(self): self.tryImport('cdutil')
    def testGenutil(self): self.tryImport('genutil')
    def testRegrid(self): self.tryImport('regrid')


if __name__ == '__main__':
    unittest.main()
