"""
This test exposes a bug in 64-bit Numeric.  Attributes are reported
as arrays of arrays of scalars.

This test is deactivated for now because I've worked around the problem in cdscan.

"""

import unittest, pkg_resources, cdms, sys
import Numeric


class _AttribTest(unittest.TestCase):
    def setUp(self):
        f = pkg_resources.resource_filename('cdat_lite.test', self.testfile)
        d = cdms.open(f)
        self.value = d.attributes[self.attrib]
        
    def testAttribType(self):
        # This should be true in both 64-bit and 32-bit versions
        assert type(self.value) == Numeric.ArrayType

    def testAttribNesting(self):
        # This is only true in 32-bit versions
        assert type(self.value[0]) == int
    
#class PPAtribTest(_AttribTest):
#    testfile = 'testpp.pp'
#    attrib = 'input_word_length'

#class NCAttribTest(_AttribTest):
#    testfile = 'foo.nc'
#    attrib = 'bar'

