#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py install

This script compiles libcdms.a and and a few essential CDAT packages
then installs them.  If you want to install it locally to your home
directory use virtual_python.py.
"""


import sys, os, glob

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension
from setuptools.command.install import install
from setup_util import MyBuild_ext, MyBuild


long_description = """
= CDAT-lite =

This package contains core components from the Climate Data Analysis Tools (CDAT)
with slight modifications to make them compatable with python eggs.  The cdms package
has been augmented with code to read UK Met. Office PP file format developed at the
British Atmospheric Data Centre.

Full documentation for CDAT is available from http://cdat.sf.net.
"""

# Numeric is a difficult case to get to work with setuptools.  As a
# legacy package it isn't easily findable from sourceforge, therefore
# easy_install fails to download it on demand.  To complicate things
# further we need to know where the headers to build the C modules but
# the setup_requires keyword to setup() doesn't appear to work if
# Numeric is installed but not an egg.  Here we only require Numeric
# if it isn't installed already and the setup_util.MyBuild_ext handles
# finding the headers.  In the end we should brobably distribute our
# own Numeric egg.
try:
    import Numeric
    requires = []
except ImportError:
    requires = ['Numeric']

def makeExtension(name, package_dir=None, sources=None,
                  include_dirs=None, library_dirs=None, libraries=None):
    """Convenience function for building extensions.
    """

    if not package_dir:
        package_dir = name
    if not sources:
        sources = glob.glob('Packages/%s/Src/*.c' % package_dir)
    if not include_dirs:
        include_dirs = ['Packages/%s/Include' % package_dir, 'libcdms/include']
    if not library_dirs:
        library_dirs = ['Packages/%s/Lib' % package_dir, 'libcdms/lib']
    if not libraries:
        libraries = ['cdms', 'netcdf']

    e = Extension(name, sources,
                  include_dirs=include_dirs,
                  library_dirs=library_dirs,
                  libraries=libraries)

    return e

def linkScripts(scripts=['cdscan']):
    """In order to put cdat scripts in their own package they are symbolically
    linked into the cdat_scripts directory.
    """
    for script in scripts:
        src = os.path.abspath(os.path.join('libcdms/src/python', script))
        dest = os.path.abspath(os.path.join('cdat_scripts', script+'.py'))
        if not os.path.exists(dest):
            os.symlink(src, dest)
    


#------------------------------------------------------------------------------

linkScripts()
    
setup(name='cdat-lite',
      description="Climate Data Analysis tools, core components",
      long_description=long_description,
      #!TODO: How do we sync this with the current CDAT version?
      # Will need fixing when I decide whether to use a remote CDAT tree.
      version="4.0_cdunifpp0.7",
      url = 'http://www.badc.rl.ac.uk',

      dependency_links = ['.'],
      setup_requires = requires,
      install_requires = requires + ['setuptools>=0.6c1'],

      
      packages = ['unidata', 'cdms', 'cdutil', 'xmgrace', 'genutil',
                  'PropertiedClasses', 'regrid', 'cdat_scripts'],
      py_modules = ['MV'],
      package_dir = {'': 'Packages/cdms',
                     'unidata': 'Packages/unidata/Lib',
                     'cdms': 'Packages/cdms/Lib',
                     'cdutil': 'Packages/cdutil/Lib',
                     'xmgrace': 'Packages/xmgrace/Lib',
                     'genutil': 'Packages/genutil/Lib',
                     'PropertiedClasses': 'Packages/Properties/Lib',
                     'regrid': 'Packages/regrid/Lib',
                     'cdat_scripts': 'cdat_scripts'
                     },
      
      ext_modules = [
        makeExtension('cdtime'),
        makeExtension('unidata.udunits_wrap', 'unidata'),
        makeExtension('cdms.Cdunif', 'cdms',
                      ['Packages/cdms/Src/Cdunifmodule.c']),
        Extension('cdms._bindex',
                  ['Packages/cdms/Src/_bindexmodule.c',
                   'Packages/cdms/Src/bindex.c']),
        makeExtension('genutil.array_indexing', 'genutil', library_dirs=[], libraries=[]),
        Extension('regrid._regrid', ['Packages/regrid/Src/_regridmodule.c']),
        Extension('regrid._scrip', ['Packages/regrid/Src/_scripmodule.c',
                                    'Packages/regrid/Src/regrid.c'])
        ],

      # Since udunits.dat isn't in the Lib directory we use the data_files attribute
      # to install data.
      #include_package_data = True,
      #package_data = {'unidata': ['Packages/unidata/Src/*.dat']},
      data_files = [('unidata', ['Packages/unidata/Src/udunits.dat'])],
      
      entry_points = {
        'console_scripts': ['cdscan = cdat_scripts:cdscan_main']
        },
      
      cmdclass = {'build_ext': MyBuild_ext}
      )

