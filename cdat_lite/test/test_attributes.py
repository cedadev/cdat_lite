"""
This test exposes a bug in 64-bit cdunif.  Attributes are reported
as arrays of arrays of scalars.

"""

import unittest, pkg_resources, cdms, sys
import Numeric

def _testFactory(testfile, attrib):
    class AttribTest(unittest.TestCase):
        def setUp(self):
            f = pkg_resources.resource_filename('cdat_lite.test', testfile)
            d = cdms.open(f)
            self.value = d.attributes[attrib]

        def testInputWordLength1(self):
            # This should be true in both 64-bit and 32-bit versions
            assert type(self.value) == Numeric.ArrayType

        def testInputWordLength2(self):
            # This is only true in 32-bit versions
            assert type(self.value[0]) == int

    return AttribTest

PPAttribTest = _testFactory('testpp.pp', 'input_word_length')
NcAttribTest = _testFactory('foo.nc', 'bar')
