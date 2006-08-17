#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py install

This script compiles libcdms.a and and a few essential CDAT packages
then installs them.  If you want to install it locally to your home
directory use virtual_python.py.
"""

#---------------------------------------------------------------------------------
# Configuration.
#

# Netcdf will be autodetected if in a standard place.
NETCDF_PREFIX = '/research/callisto/spascoe/netcdf'

#--------------------------------------------------------------------------------



import sys, os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension
from setuptools.command.install import install
from distutils.command.build import build


class ConfigError(Exception):
    """Configuration failed."""
    pass

def buildLibcdms(netcdf_include, netcdf_lib):
    os.system('cd libcdms ; '
                 'CFLAGS=-fPIC ./configure --disable-drs --disable-hdf --disable-dods '
                 '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                 % (netcdf_include, netcdf_include, netcdf_lib))
    os.system('cd libcdms ; make db_util ; make cdunif')

def findNetcdfPrefix():
    for dir in ('/usr', '/usr/local', os.getenv('HOME')):
        if os.path.exists('%s/lib/libnetcdf.a' % dir):
            return dir
    raise ConfigError, ("Failed to find netcdf libraries in a standard place.  "
                        "Please define NETCDF_PREFIX.")

#--------------------------------------------------------------------------------


# Top level namespace package.
# This ensures Numeric is installed.

## setup(name = 'cdat-lite',
##       author="Stephen Pascoe",
##       version="0.1",
##       description = "An Eggable distribution of core components from PCMDI's CDAT tools (http://cdat.sourceforge.net)",
##       url = "http://www.badc.rl.ac.uk",
##       install_requires = ['Numeric>=23.0'],
##       dependency_links = ['http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=1351'],
##       namespace_packages = ['ndg'],
##       packages = ['ndg', 'ndg.cdatlite'],
##       package_dir = {'ndg.cdatlite': 'lib/ndg/cdatlite',
##                      'ndg': 'lib/ndg'
##                      },
##       )


# Unfortunately we need to import Numeric_include before we start building
# so setuptools dependency autodownloading won't work.
# Execute easy_install directly instead.
import pkg_resources, site
easy_install = pkg_resources.load_entry_point('setuptools', 'console_scripts',
                                              'easy_install')
easy_install(['Numeric'])
# We need to do this to refresh sys.path
reload(site)


try:
    NETCDF_PREFIX
except:
    NETCDF_PREFIX = findNetcdfPrefix()
    
## try:
##     NUMERIC_INCLUDE
## except:
##     try:
##         from Numeric_headers import get_numeric_include
##         NUMERIC_INCLUDE = get_numeric_include()
##     except:
##         raise ConfigError, ("Failed to find Numeric header files.  "
##                             "Please define NUMERIC_INCLUDE.")

from Numeric_headers import get_numeric_include
NUMERIC_INCLUDE = get_numeric_include()

CDUNIF_INCDIRS = ['libcdms/include', NETCDF_PREFIX+'/include', NUMERIC_INCLUDE]
CDUNIF_LIBDIRS = ['libcdms/lib', NETCDF_PREFIX+'/lib']
CDUNIF_LIBS = ['cdms', 'netcdf']

#--------------------------------------------------------------------------------



buildLibcdms(NETCDF_PREFIX+'/include', NETCDF_PREFIX+'/lib')

setup (name = "cdutil",
       author="PCMDI Software Team",
       version='4.0',
       description = "Utilities for climate data manipulation",
       url = "http://cdat.sourceforge.net",
       install_requires = ['Numeric>=23.0'],
       packages = ['cdutil'],
       package_dir = {'cdutil': 'Packages/cdutil/Lib'},
      )

setup (name = "cdtime",
       description = "Time utilities",
       version='3.2',
       url = "http://cdat.sf.net",
       install_requires = ['Numeric>=23.0'],
       include_dirs = ['Packages/cdtime/Include'] + CDUNIF_INCDIRS,
       ext_modules = [Extension('cdtime',
                       ['Packages/cdtime/Src/cdtimemodule.c'],
                       library_dirs = CDUNIF_LIBDIRS,
                       libraries = CDUNIF_LIBS)
       ]
)


setup (name = "udunits",
       version='1.0',
       author='doutriaux1@llnl.gov',
       description = "Python wrapping for UDUNITS package developped by UNIDATA",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['unidata'],
       package_dir = {'unidata': 'Packages/unidata/Lib'},
       package_data = {'unidata': ['Packages/unidata/Src/*.dat']},
       ext_modules = [
         Extension('unidata.udunits_wrap',
                   ['Packages/unidata/Src/udunits_wrap.c',
                    'Packages/unidata/Src/utparse.c',
                    'Packages/unidata/Src/utlib.c',
                    'Packages/unidata/Src/utscan.c',
                    ],
                   include_dirs = ['Packages/unidata/Include'] + CDUNIF_INCDIRS
                   )
         ]
       )


setup (name = "cdms",
       version='3.2',
       description = "Climate Data Management System",
       url = "http://cdat.sf.net",
       packages = ['cdms'],
       py_modules = ['MV'],
       package_dir = {'cdms': 'Packages/cdms/Lib',
                      'MV': 'Packages/cdms'},
       include_dirs = ['Packages/cdms/Include'] + CDUNIF_INCDIRS,
       ext_modules = [Extension('cdms.Cdunif',
                                ['Packages/cdms/Src/Cdunifmodule.c'],
                                library_dirs = CDUNIF_LIBDIRS,
                                libraries = CDUNIF_LIBS,
                                ),
                      Extension('cdms._bindex',
                                ['Packages/cdms/Src/_bindexmodule.c',
                                 'Packages/cdms/Src/bindex.c'],
                                )
                      ]
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
      )

setup (name = "cdat",
       version='4.0',
       author='PCMDI',
       description = "General utilities for scientific computing",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['genutil'],
       package_dir = {'genutil': 'Packages/genutil/Lib'},
       include_dirs = CDUNIF_INCDIRS,
       ext_modules = [
    Extension('genutil.array_indexing',
              ['Packages/genutil/Src/array_indexing.c',]
              ),

    ]
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
      )

setup (name = "regrid",
       version='3.3',
       description = "Remap Package",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['regrid'],
       package_dir = {'regrid': 'Packages/regrid/Lib'},
       include_dirs = CDUNIF_INCDIRS,
       ext_modules = [Extension('regrid._regrid', ['Packages/regrid/Src/_regridmodule.c']),
                      Extension('regrid._scrip', ['Packages/regrid/Src/_scripmodule.c','Packages/regrid/Src/regrid.c'])]
      )

