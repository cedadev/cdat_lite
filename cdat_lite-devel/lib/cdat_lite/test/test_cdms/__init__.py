"""
Run tests taken from CDAT/Packages/cdms/Test.

"""

from pkg_resources import resource_stream
from unittest import TestCase
import tempfile, os, shutil

import cdms2

class CdTest(TestCase):
    """
    Run all tests taken from CDAT's cdms package
    
    """

    @classmethod
    def addTestModule(cls, module):
        name = 'test_%s' % module
        def f(self):
            self.runTest(module)
        f.__name__ = name
        
        setattr(cls, name, f)

    @classmethod
    def addFullTestModule(cls, module):
        name = 'fulltest_%s' % module
        def f(self):
            self.runTest(module)
        f.__name__ = name
        
        setattr(cls, name, f)


    @classmethod
    def addTestModules(cls, modules):
        for m in modules:
            cls.addTestModule(m)


    @classmethod
    def addFullTestModules(cls, modules):
        for m in modules:
            cls.addFullTestModule(m)
    
    def setUp(self):
        """
        Move to a temporary directory before executing the test module.
        """
        self._tmpdir = tempfile.mkdtemp('.tmp', 'test_cdms')
        os.chdir(self._tmpdir)

        # Enter NetCDF4 mode for these tests
        #!TODO: magically deactivate test if compiled with NetCDF3
        cdms2.setNetcdfShuffleFlag(1)
        cdms2.setNetcdfDeflateFlag(1)
        cdms2.setNetcdfDeflateLevelFlag(0)


    def runTest(self, module):
        fh = resource_stream('cdat_lite.test.test_cdms',
                             module+'.py')
        context = globals().copy()
        exec fh in context

    def tearDown(self):
        shutil.rmtree(self._tmpdir)
            
CdTest.addTestModules(['cdtest01', 'cdtest02', 'cdtest03', 'cdtest04',
                       'cdtest05', 'cdtest06', 'cdtest07', 'cdtest08',
                       #'cdtest09',
                       'cdtest10',
                       'cdtest11', 'cdtest12', 'cdtest13', 'cdtest14',
                       ])
CdTest.addFullTestModules(['cdtest18'])

