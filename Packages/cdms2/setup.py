#!/usr/bin/env python
from distutils.core import setup, Extension
import os, sys
target_prefix = sys.prefix
for i in range(len(sys.argv)):
    a = sys.argv[i]
    if a=='--prefix':
        target_prefix=sys.argv[i+1]
    sp = a.split("--prefix=")
    if len(sp)==2:
        target_prefix=sp[1]
        print 'Target is:',target_prefix
sys.path.insert(0,os.path.join(target_prefix,'lib','python%i.%i' % sys.version_info[:2],'site-packages')) 
import cdat_info
import numpy

setup (name = "cdms2",
       version='5.0',
       description = "Climate Data Management System, Numpy version",
       url = "http://cdat.sf.net",
       packages = ['cdms2'],
       package_dir = {'cdms2': 'Lib'},
       include_dirs = ['Include', numpy.lib.utils.get_include()] + cdat_info.cdunif_include_directories,
       scripts = ['Script/convertcdms.py'],
       ext_modules = [Extension('cdms2.Cdunif',
                                ['Src/Cdunifmodule.c'],
                                library_dirs = cdat_info.cdunif_library_directories,
                                libraries = cdat_info.cdunif_libraries,
                                ),
                      Extension('cdms2._bindex',
                                ['Src/_bindexmodule.c', 'Src/bindex.c'],
                                ) 
                     ]
      )

setup (name = "MV2",
       version = '1.0',
       description="Alias for cdms2.MV",
       url = "http://cdat.sf.net",
       py_modules=['MV2']
       )
