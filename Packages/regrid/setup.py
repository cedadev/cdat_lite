#!/usr/bin/env python
from distutils.core import setup, Extension
import os, sys
setup (name = "regrid",
       version='3.3',
       description = "Remap Package",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['regrid'],
       package_dir = {'regrid': 'Lib'},
       ext_modules = [Extension('regrid._regrid', ['Src/_regridmodule.c']),
                      Extension('regrid._scrip', ['Src/_scripmodule.c','Src/regrid.c'])]
      )
    
