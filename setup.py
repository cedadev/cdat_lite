#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py install

This script compiles libcdms.a and and a few essential CDAT packages
then installs them.  If you want to install it locally to your home
directory use virtual_python.py.
"""

import sys, os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension
from setuptools.command.install import install
from distutils.command.build import build

def buildLibcdms(netcdf_include, netcdf_lib):
    os.system('cd libcdms ; '
                 './configure --disable-drs --disable-hdf --disable-dods '
                 '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                 % (netcdf_include, netcdf_include, netcdf_lib))
    os.system('cd libcdms ; make db_util ; make cdunif')

packages = []
package_dir = {}
py_modules = []

# cdutil
packages.append('cdutil')
package_dir['cdutil'] = 'Packages/cdutil/Lib'
package_data = {}

# cdtime
extensions.append(Extension('cdtime',
                            ['Packages/cdtime/Src/cdtimemodule.c'],
                            include_dirs = ['Packages/cdtime/Include'] + cdunif_include_dirs,
                            library_dirs = cdunif_library_dirs,
                            libraries = cdat_info.cdunif_libs))

# unidata
packages.append('unidata')
package_dir['unidata'] = 'Packages/unidata/Lib'
package_data['unidata'] = ['Packages/unidata/Src/*.dat']
extensions.append(Extension('unidata.udunits_wrap',
                            ['Packages/unidata/Src/udunits_wrap.c',
                             'Packages/unidata/Src/utparse.c',
                             'Packages/unidata/Src/utlib.c',
                             'Packages/unidata/Src/utscan.c',
                             ],
                            include_dirs = ['Packages/unidata/Include'],
                            ))

# cdms
packages.append('cdms')
package_dir['cdms'] = 'Packages/cdms/Lib'
package_dir['MV'] = 'Packages/cdms'
py_modules.append('MV')
extensions += [
    Extension('cdms.Cdunif',
              ['Packages/cdms/Src/Cdunifmodule.c'],
              include_dirs = ['Packages/cdms/Include'] + cdunif_include_dirs,
              library_dirs = cdunif_library_dirs,
              libraries = cdunif_libs,
              ),
    Extension('cdms._bindex',
              ['Packages/cdms/Src/_bindexmodule.c', 'Packages/cdms/Src/bindex.c'],
              include_dirs = ['Packages/cdms/Include'] + cdunif_include_dirs
              )
    ]

# xmgrace
packages.append('xmgrace')
package_dir['xmgrace'] = 'Packages/xmgrace/Lib'

# genutil
packages.append('genutil')
package_dir['genutil'] = 'Packages/genutil/Lib'
extensions.append(Extension('genutil.array_indexing', ['Packages/genutil/Src/array_indexing.c']))

# Properties
packages.append('PropertiedClasses')
package_dir['PropertiedClasses'] = 'Packages/Properties/Lib'

# regrid
packages.append('regrid')
package_dir['regrid'] = 'Packages/regrid/Lib'
extensions += [
    Extension('regrid._regrid', ['Packages/regrid/Src/_regridmodule.c']),
    Extension('regrid._scrip', ['Packages/regrid/Src/_scripmodule.c','Packages/regrid/Src/regrid.c'])
    ]



setup(name = 'cdat-lite',
      author="PCMDI Software Team -- repackaged by the BADC",
      version="4.0",
      description = "An Eggable distribution of core components from PCMDI's CDAT tools (http://cdat.sourceforge.net)",
      url = "http://www.badc.rl.ac.uk",
      packages = packages,
      package_dir = package_dir,
      py_modules = py_modules,
      extensions = extensions,
      cmdclass = {'install': MyInstall}
      )

