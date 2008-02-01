"""
Run tests taken from CDAT/Packages/cdms/Test.

"""

from pkg_resources import resource_stream
from unittest import TestCase
import tempfile, os, shutil


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
    def addTestModules(cls, modules):
        for m in modules:
            cls.addTestModule(m)
    
    def setUp(self):
        """
        Move to a temporary directory before executing the test module.
        """
        self._tmpdir = tempfile.mkdtemp('.tmp', 'test_cdms')
        os.chdir(self._tmpdir)

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
                       'cdtest11', 'cdtest12', 'cdtest13', 'cdtest14'])

