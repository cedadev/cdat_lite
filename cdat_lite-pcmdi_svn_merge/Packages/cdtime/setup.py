#!/usr/bin/env python
from distutils.core import setup, Extension
import os, sys
import cdat_info
setup (name = "cdtime",
       description = "Time utilities",
       version='3.2',
       url = "http://cdat.sf.net",
       include_dirs = ['Include'] + cdat_info.cdunif_include_directories,
       ext_modules = [Extension('cdtime', 
                       ['Src/cdtimemodule.c'],
                       library_dirs = cdat_info.cdunif_library_directories,
                       libraries = cdat_info.cdunif_libraries)
       ]
)
    
