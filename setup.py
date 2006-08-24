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

# Numeric is a difficult case to get to work with setuptools.
# As a legacy package it isn't easily findable from sourceforge, therefore easy_install
# fails to download it on demand.  To complicate things further we need to know where
# the headers to build the C modules.  setup_util.MyBuild_ext deals with this problem.
# Here we only require Numeric if it isn't installed already.
# In the end we should brobably distribute our own Numeric egg.
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


setup(name='cdat-lite',
      description="Climate Data Analysis tools, core components",
      long_description=long_description,
      #!TODO: How do we sync this with the current CDAT version?
      # Will need fixing when I decide whether to use a remote CDAT tree.
      version="4.6-ppio",
      url = 'http://www.badc.rl.ac.uk',
      
      setup_requires = requires,
      install_requires = requires + ['setuptools>=0.6'],

      packages = ['unidata', 'cdms', 'cdutil', 'xmgrace', 'genutil',
                  'PropertiedClasses', 'regrid'],
      py_modules = ['MV'],
      package_dir = {'': 'Packages/cdms',
                      'unidata': 'Packages/unidata/Lib',
                      'cdms': 'Packages/cdms/Lib',
                      'cdutil': 'Packages/cdutil/Lib',
                      'xmgrace': 'Packages/xmgrace/Lib',
                      'genutil': 'Packages/genutil/Lib',
                      'PropertiedClasses': 'Packages/Properties/Lib',
                      'regrid': 'Packages/regrid/Lib',
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

       cmdclass = {'build_ext': MyBuild_ext}
      )

sys.exit()

#--------------------------------------------------------------------------------

setup (name = "cdtime",
       description = "Time utilities",
       version='3.2',
       url = "http://cdat.sf.net",
       setup_requires = ['Numeric>=23.0'],
       install_requires = ['Numeric>=23.0'],
       ext_modules = [Extension('cdtime',
                       ['Packages/cdtime/Src/cdtimemodule.c'],
                                include_dirs = ['Packages/cdtime/Include', 'libcdms/include'],
                                library_dirs = ['libcdms/lib'],
                                libraries = ['cdms', 'netcdf']
                                )
                      ],
       cmdclass = {'build': MyBuild,
                   'build_ext': MyBuild_ext}
       )

setup (name = "udunits",
       version='1.0',
       author='doutriaux1@llnl.gov',
       description = "Python wrapping for UDUNITS package developped by UNIDATA",
       url = "http://www-pcmdi.llnl.gov/software",
       setup_requires = ['Numeric>=23.0'],
       install_requires = ['Numeric>=23.0'],

       packages = ['unidata'],
       package_dir = {'unidata': 'Packages/unidata/Lib'},

       # Since udunits.dat isn't in the Lib directory we use the data_files attribute
       # to install data.
       #include_package_data = True,
       #package_data = {'unidata': ['Packages/unidata/Src/*.dat']},
       data_files = [('unidata', ['Packages/unidata/Src/udunits.dat'])],

       ext_modules = [
         Extension('unidata.udunits_wrap',
                   ['Packages/unidata/Src/udunits_wrap.c',
                    'Packages/unidata/Src/utparse.c',
                    'Packages/unidata/Src/utlib.c',
                    'Packages/unidata/Src/utscan.c',
                    ],
                   include_dirs = ['Packages/unidata/Include']
                   )
         ],
       cmdclass = {'build': MyBuild,
                   'build_ext': MyBuild_ext}
       )


setup (name = "cdms",
       version='3.2',
       description = "Climate Data Management System",
       url = "http://cdat.sf.net",
       setup_requires = ['Numeric>=23.0'],
       install_requires = ['Numeric>=23.0'],
       packages = ['cdms'],
       py_modules = ['MV'],
       package_dir = {'cdms': 'Packages/cdms/Lib',
                      'MV': 'Packages/cdms'},
       ext_modules = [Extension('cdms.Cdunif',
                                ['Packages/cdms/Src/Cdunifmodule.c'],
                                include_dirs = ['Packages/cdms/Include', 'libcdms/include'],
                                library_dirs = ['libcdms/lib'],
                                libraries = ['cdms', 'netcdf'],
                                ),
                      Extension('cdms._bindex',
                                ['Packages/cdms/Src/_bindexmodule.c',
                                 'Packages/cdms/Src/bindex.c'],
                                )
                      ],
       cmdclass = {'build': MyBuild,
                   'build_ext': MyBuild_ext}
       )

setup (name = "cdutil",
       author="PCMDI Software Team",
       version='4.0',
       description = "Utilities for climate data manipulation",
       url = "http://cdat.sourceforge.net",
       packages = ['cdutil'],
       package_dir = {'cdutil': 'Packages/cdutil/Lib'},
       cmdclass = {'build': MyBuild}
      )


#setup (name = "MV",
#       version = '1.0',
#       description="Alias for cdms.MV",
#       url = "http://cdat.sf.net",
#       namespace_packages = ['ndg', 'ndg.cdatlite'],
#       py_modules=['ndg.cdatlite.MV'],
#       package_dir = {'ndg.cdatlite.MV': 'Packages/cdms'}
#       )

setup (name = "xmgrace",
       version='1.1',
       author='doutriaux1@llnl.gov',
       description = "wrapping package for xmgrace",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['xmgrace'],
       package_dir = {'xmgrace': 'Packages/xmgrace/Lib'},
       cmdclass = {'build': MyBuild}
      )

setup (name = "cdat",
       version='4.0',
       author='PCMDI',
       description = "General utilities for scientific computing",
       url = "http://www-pcmdi.llnl.gov/software",
       setup_requires = ['Numeric>=23.0'],
       install_requires = ['Numeric>=23.0'],
       packages = ['genutil'],
       package_dir = {'genutil': 'Packages/genutil/Lib'},
       ext_modules = [
    Extension('genutil.array_indexing',
              ['Packages/genutil/Src/array_indexing.c'],
              include_dirs = ['libcdms/include'],
              ),

    ],
       cmdclass = {'build': MyBuild, 'build_ext': MyBuild_ext}
      )

execfile(os.path.join('Packages/Properties/Lib', 'Properties_version.py'))
setup (name = "PropertiedClasses",
       version=version,
       author="Paul F. Dubois",
       description = "Properties",
       maintainer = "Numerical Python Developers",
       maintainer_email = "numpy-developers@lists.sourceforge.net",
       url = "http://sourceforge.net/projects/numpy",
       packages = ['PropertiedClasses'],
       package_dir = {'PropertiedClasses': 'Packages/Properties/Lib'},
       cmdclass = {'build': MyBuild, 'build_ext': MyBuild_ext}
      )

setup (name = "regrid",
       version='3.3',
       description = "Remap Package",
       url = "http://www-pcmdi.llnl.gov/software",
       setup_requires = ['Numeric>=23.0'],
       install_requires = ['Numeric>=23.0'],
       packages = ['regrid'],
       package_dir = {'regrid': 'Packages/regrid/Lib'},
       include_dirs = ['libcdms/include'],
       ext_modules = [Extension('regrid._regrid', ['Packages/regrid/Src/_regridmodule.c']),
                      Extension('regrid._scrip', ['Packages/regrid/Src/_scripmodule.c','Packages/regrid/Src/regrid.c'])],
       cmdclass = {'build': MyBuild, 'build_ext': MyBuild_ext}       
      )

