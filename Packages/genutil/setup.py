from distutils.core import setup, Extension
import os,sys,string
import numpy

setup (name = "cdat",
       version='4.0',
       author='PCMDI',
       description = "General utilities for scientific computing",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['genutil'],
       package_dir = {'genutil': 'Lib'},
       include_dirs = [numpy.lib.utils.get_include()],
       ext_modules = [
    Extension('genutil.array_indexing',
              ['Src/array_indexing.c',]
              ),
    
    ]
      )

