"""
This test exposes a bug in 64-bit cdunifpp.  Attributes are reported
as arrays of arrays of scalars.

"""

import unittest, pkg_resources, cdms, sys
import Numeric

class PPAttribTest(unittest.TestCase):
    def setUp(self):
        f = pkg_resources.resource_filename('cdat_lite.test', 'testpp.pp')
        self.d = cdms.open(f)

    def testInputWordLength1(self):
        # This should be true in both 64-bit and 32-bit versions
        assert type(self.d.input_word_length) == Numeric.ArrayType

    def testInputWordLength2(self):
        # This is only true in 32-bit versions
        assert type(self.d.input_word_length[0]) == int
