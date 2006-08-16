from distutils.core import setup

setup (name = "cdutil",
       author="PCMDI Software Team",
       version='4.0',
       description = "Utilities for climate data manipulation",
       url = "http://cdat.sourceforge.net",
       packages = ['cdutil'],
       package_dir = {'cdutil': 'Lib'},
      )
    
