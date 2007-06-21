#!/usr/bin/env python
"""Build the cdat_lite distribution.
"""


import sys, os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension
from setup_util import build_ext, makeExtension


NDG_EGG_REPOSITORY = 'http://ndg.nerc.ac.uk/dist/'
CDAT_LITE_URL = 'http://proj.badc.rl.ac.uk/ndg/wiki/CdatLite'
CDAT_LICENCE_URL = 'http://www-pcmdi.llnl.gov/software-portal/cdat/docs/cdat-license'
CDAT_HOME_URL = 'http://www-pcmdi.llnl.gov/software-portal/cdat'

# cdat-lite versioning is complicated as it is a repackage of cdat-cdunifpp.  There are
# therefore 3 version numbers to consider: CDAT, cdunifpp and cdat-lite.  Once we start
# using versions of CDAT from the PCMDI SVN the version string could become very long
# indeed therefore the following strategy is used:
#
#  1. Eggs are quoted with the version: <cdat-release>-<cdat-lite-version>
#  2. If a PCMDI SVN version of CDAT is used it is stated in long_description not
#     in <cdat-release>.
#  3. The cdunifpp version is stated in long_description not in the version.  Any
#     change to the cdunifpp version naturally triggers a new <cdat-lite-version>.
cdat_release = '4.1.2'
cdat_tag = '-r5752'
cdunifpp_version = '0.8'
cdat_lite_version = '0.2.2'


long_description = """
This package contains core components from the Climate Data Analysis
Tools (CDAT) with slight modifications to make them compatable with
python eggs.  The cdms package has been augmented with the latest code
to read UK Met. Office PP file format developed at the British
Atmospheric Data Centre.

This software is based on CDAT-%(cdat_release)s%(cdat_tag)s and
cdunfpp%(cdunifpp_version)s.  It is distributed under the CDAT licence
%(CDAT_LICENCE_URL)s.

Full documentation for CDAT is available from the CDAT homepage
%(CDAT_HOME_URL)s.

""" % globals()

#------------------------------------------------------------------------------

def linkScripts(scripts=['cdscan']):
    """In order to put cdat scripts in their own package they are symbolically
    linked into the cdat/scripts directory.
    """
    for script in scripts:
        src = os.path.abspath(os.path.join('libcdms/src/python', script))
        dest = os.path.abspath(os.path.join('cdat_lite', 'scripts', script+'.py'))
        if not os.path.exists(dest):
            os.symlink(src, dest)
linkScripts()

#------------------------------------------------------------------------------
    
setup(name='cdat_lite',
      description="Climate Data Analysis tools, core components",
      long_description=long_description,
      version='%s-%s' % (cdat_release, cdat_lite_version),
      url = CDAT_LITE_URL,
      download_url = NDG_EGG_REPOSITORY,
      maintainer = 'Stephen Pascoe',
      maintainer_email = 'S.Pascoe@rl.ac.uk',
      license = CDAT_LICENCE_URL,

      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        ],
        

      dependency_links = [NDG_EGG_REPOSITORY],
      setup_requires = ['Numeric'],
      install_requires = ['setuptools>=0.6c1', 'Numeric>=24.2'],
      zip_safe = False,
      
      packages = ['unidata', 'cdms', 'cdutil', 'xmgrace', 'genutil',
                  'PropertiedClasses', 'regrid', 
                  'cdat_lite', 'cdat_lite.clib', 'cdat_lite.scripts', 'cdat_lite.test'],
      py_modules = ['MV'],
      package_dir = {'': 'Packages/cdms',
                     'unidata': 'Packages/unidata/Lib',
                     'cdms': 'Packages/cdms/Lib',
                     'cdutil': 'Packages/cdutil/Lib',
                     'xmgrace': 'Packages/xmgrace/Lib',
                     'genutil': 'Packages/genutil/Lib',
                     'PropertiedClasses': 'Packages/Properties/Lib',
                     'regrid': 'Packages/regrid/Lib',
                     'cdat_lite': 'cdat_lite',
                     'cdat_lite.scripts': 'cdat_lite/scripts',
                     'cdat_lite.clib': 'cdat_lite/clib',
                     'cdat_lite.test': 'cdat_lite/test'
                     },
      
      ext_modules = [
        makeExtension('cdtime'),
        makeExtension('unidata.udunits_wrap', 'unidata'),
        makeExtension('cdms.Cdunif', 'cdms',
                      ['Packages/cdms/Src/Cdunifmodule.c']),
        Extension('cdms._bindex',
                  ['Packages/cdms/Src/_bindexmodule.c',
                   'Packages/cdms/Src/bindex.c'],
                  ),
        makeExtension('genutil.array_indexing', 'genutil'),
        Extension('regrid._regrid', ['Packages/regrid/Src/_regridmodule.c'],
                  ),
        Extension('regrid._scrip', ['Packages/regrid/Src/_scripmodule.c',
                                    'Packages/regrid/Src/regrid.c'],
                  )
        ],

      # Since udunits.dat isn't in the Lib directory we use the data_files attribute
      # to install data.
      include_package_data = True,
      package_data = {'cdat_lite.clib': ['include/*', 'lib/*']},
      #package_data = {'unidata': ['Packages/unidata/Src/*.dat']},
      data_files = [('unidata', ['Packages/unidata/Src/udunits.dat'])],
      
      entry_points = {
        'console_scripts': ['cdscan = cdat_lite.scripts:cdscan_main']
        },

      test_suite = 'nose.collector',
      
      cmdclass = {'build_ext': build_ext}
      )

    

