from distutils.core import setup, Extension
import os,sys,string


setup (name = "cdat",
       version='4.0',
       author='PCMDI',
       description = "General utilities for scientific computing",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['genutil'],
       package_dir = {'genutil': 'Lib'},
       ext_modules = [
    Extension('genutil.array_indexing',
              ['Src/array_indexing.c',]
              ),
    
    ]
      )

