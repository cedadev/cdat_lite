"""
Run tests taken from CDAT/Packages/cdms/Test.

"""

from pkg_resources import resource_filename
from unittest import TestCase
import imp


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
    
    def runTest(self, module):
        imp.load_module(module, *imp.find_module('%s.%s' % (__name__, module)))
        
            
CdTest.addTestModules(['cdtest01', 'cdtest02', 'cdtest03', 'cdtest04',
                       'cdtest05', 'cdtest06', 'cdtest07', 'cdtest08',
                       'cdtest09', 'cdtest10',
                       'cdtest11', 'cdtest12', 'cdtest13', 'cdtest14'])

