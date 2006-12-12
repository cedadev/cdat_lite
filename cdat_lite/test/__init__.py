"""
Run all tests.

@author: Stephen Pascoe
"""

import unittest
import test_import, test_cdms
test_modules = [test_import, test_cdms]

loader = unittest.defaultTestLoader
suite = unittest.TestSuite()
for mod in test_modules:
    suite.addTests(loader.loadTestsFromModule(mod))


def main(args = None):
    if not args:
        args = sys.argv[1:]

    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    main()
