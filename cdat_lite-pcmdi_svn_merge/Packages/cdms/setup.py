#!/usr/bin/env python
from distutils.core import setup, Extension
import os, sys
import cdat_info

setup (name = "cdms",
       version='3.2',
       description = "Climate Data Management System",
       url = "http://cdat.sf.net",
       packages = ['cdms'],
       package_dir = {'cdms': 'Lib'},
       include_dirs = ['Include'] + cdat_info.cdunif_include_directories,
       ext_modules = [Extension('cdms.Cdunif',
                                ['Src/Cdunifmodule.c'],
                                library_dirs = cdat_info.cdunif_library_directories,
                                libraries = cdat_info.cdunif_libraries,
                                ),
                      Extension('cdms._bindex',
                                ['Src/_bindexmodule.c', 'Src/bindex.c'],
                                ) 
                     ]
      )

setup (name = "MV",
       version = '1.0',
       description="Alias for cdms.MV",
       url = "http://cdat.sf.net",
       py_modules=['MV']
       )
