from distutils.core import setup, Extension
import os,sys,string


setup (name = "udunits",
       version='1.0',
       author='doutriaux1@llnl.gov',
       description = "Python wrapping for UDUNITS package developped by UNIDATA",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['unidata'],
       package_dir = {'unidata': 'Lib'},
       package_data = {'unidata': ['Src/udunits.dat']},
       ext_modules = [
    Extension('unidata.udunits_wrap',
              ['Src/udunits_wrap.c',
               'Src/utparse.c',
               'Src/utlib.c',
               'Src/utscan.c',
               ],
              include_dirs = ['Include']
              )
    ]
      )
