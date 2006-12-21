#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py install

This script compiles libcdms.a and and a few essential CDAT packages
then installs them.
"""


import sys, os, glob

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension
from setup_util import build_ext, build_cdms, numericHeaders, netcdfHome


NDG_EGG_REPOSITORY = 'http://ndg.nerc.ac.uk/dist/'


# cdat-lite versioning is complicated as it is a repackage of cdat-cdunifpp.  There are
# therefore 3 version numbers to consider: CDAT, cdunifpp and cdat-lite
cdat_version = '4.0'
cdunifpp_version = '0.7'
cdat_lite_version = '0.1'

version = '%s-cdunifpp%s-%s' % (cdat_version, cdunifpp_version, cdat_lite_version)


long_description = """
= CDAT-lite =

This package contains core components from the Climate Data Analysis Tools (CDAT)
with slight modifications to make them compatable with python eggs.  The cdms package
has been augmented with code to read UK Met. Office PP file format developed at the
British Atmospheric Data Centre.

Full documentation for CDAT is available from http://cdat.sf.net.
"""

def makeExtension(name, package_dir=None, sources=None,
                  include_dirs=None, library_dirs=None, libraries=None):
    """Convenience function for building extensions.
    """

    if not package_dir:
        package_dir = name
    if not sources:
        sources = glob.glob('Packages/%s/Src/*.c' % package_dir)
    if not include_dirs:
        include_dirs = ['Packages/%s/Include' % package_dir, 'libcdms/include',
                        numericHeaders, netcdfHome+'/include']
    if not library_dirs:
        library_dirs = ['Packages/%s/Lib' % package_dir, 'libcdms/lib', netcdfHome+'/lib']
    if not libraries:
        libraries = ['cdms', 'netcdf']

    e = Extension(name, sources,
                  include_dirs=include_dirs,
                  library_dirs=library_dirs,
                  libraries=libraries)

    return e

def linkScripts(scripts=['cdscan']):
    """In order to put cdat scripts in their own package they are symbolically
    linked into the cdat/scripts directory.
    """
    for script in scripts:
        src = os.path.abspath(os.path.join('libcdms/src/python', script))
        dest = os.path.abspath(os.path.join('cdat_lite', 'scripts', script+'.py'))
        if not os.path.exists(dest):
            os.symlink(src, dest)
    


#------------------------------------------------------------------------------

linkScripts()
    
setup(name='cdat-lite',
      description="Climate Data Analysis tools, core components",
      long_description=long_description,
      #!TODO: How do we sync this with the current CDAT version?
      # Will need fixing when I decide whether to use a remote CDAT tree.
      version=version,
      url = 'http://www.badc.rl.ac.uk',

      dependency_links = [NDG_EGG_REPOSITORY],
      setup_requires = ['Numeric'],
      install_requires = ['setuptools>=0.6c1', 'Numeric>=24.2'],

      
      packages = ['unidata', 'cdms', 'cdutil', 'xmgrace', 'genutil',
                  'PropertiedClasses', 'regrid', 
                  'cdat_lite', 'cdat_lite.clib', 'cdat_lite.scripts', 'cdat_lite.test'],
      py_modules = ['MV'],
      package_dir = {'': 'Packages/cdms',
                     'unidata': 'Packages/unidata/Lib',
                     'cdms': 'Packages/cdms/Lib',
                     'cdutil': 'Packages/cdutil/Lib',
                     'xmgrace': 'Packages/xmgrace/Lib',
                     'genutil': 'Packages/genutil/Lib',
                     'PropertiedClasses': 'Packages/Properties/Lib',
                     'regrid': 'Packages/regrid/Lib',
                     'cdat_lite': 'cdat_lite',
                     'cdat_lite.scripts': 'cdat_lite/scripts',
                     'cdat_lite.clib': 'cdat_lite/clib',
                     'cdat_lite.test': 'cdat_lite/test'
                     },
      
      ext_modules = [
        makeExtension('cdtime'),
        makeExtension('unidata.udunits_wrap', 'unidata'),
        makeExtension('cdms.Cdunif', 'cdms',
                      ['Packages/cdms/Src/Cdunifmodule.c']),
        Extension('cdms._bindex',
                  ['Packages/cdms/Src/_bindexmodule.c',
                   'Packages/cdms/Src/bindex.c'],
                  include_dirs=[numericHeaders, netcdfHome+'/include']),
        makeExtension('genutil.array_indexing', 'genutil', library_dirs=[], libraries=[]),
        Extension('regrid._regrid', ['Packages/regrid/Src/_regridmodule.c'],
                  include_dirs=[numericHeaders, netcdfHome+'/include']),
        Extension('regrid._scrip', ['Packages/regrid/Src/_scripmodule.c',
                                    'Packages/regrid/Src/regrid.c'],
                  include_dirs=[numericHeaders, netcdfHome+'/include'])
        ],

      # Since udunits.dat isn't in the Lib directory we use the data_files attribute
      # to install data.
      include_package_data = True,
      package_data = {'cdat_lite.clib': ['include/*', 'lib/*']},
      #package_data = {'unidata': ['Packages/unidata/Src/*.dat']},
      data_files = [('unidata', ['Packages/unidata/Src/udunits.dat'])],
      
      entry_points = {
        'console_scripts': ['cdscan = cdat_lite.scripts:cdscan_main']
        },

      test_suite = 'cdat_lite.test.suite',
      
      cmdclass = {'build_ext': build_ext, 'build_cdms': build_cdms}
      )

