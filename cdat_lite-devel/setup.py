#!/usr/bin/env python
"""Build the cdat_lite distribution.
"""

import sys, os, shutil

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension, find_packages
from setup_util import build_ext, makeExtension, buildLibTree, copyScripts

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
cdat_release = '5.2'
cdat_tag = ''
cdunifpp_version = '0.13'



description = "Core components of the Climate Data Analysis tools.  This software is based on CDAT-%(cdat_release)s%(cdat_tag)s and cdunfpp%(cdunifpp_version)s." % globals()

long_description = open('./README').read()

#------------------------------------------------------------------------------
# Create the lib tree from traditional CDAT directory structure.
copyScripts()
buildLibTree(packageRoots={'unidata': 'Packages/unidata/Lib',
                           'cdms2': 'Packages/cdms2/Lib',
                           'cdutil': 'Packages/cdutil/Lib',
                           'xmgrace': 'Packages/xmgrace/Lib',
                           'genutil': 'Packages/genutil/Lib',
                           'Properties': 'Packages/Properties/Lib',
                           'regrid2': 'Packages/regrid2/Lib',
                           'ncml': 'Packages/ncml/Lib',
                           },
             mods=['Packages/cdms2/MV2.py', 'Packages/cdat_info.py'],
             )

#------------------------------------------------------------------------------

# As from CDAT-4.3 we must use Python-2.5.  The C extensions won't compile
# with Python-2.4 so it's best to warn the user with a sane error message now
if sys.version_info[:3] < (2,5):
    raise SystemExit("""
==========================================================================
 cdat_lite-4.3+ requires Python2.5.  If you want to use Python-2.4 please
 install cdat_lite-4.1.2.  This can be done with the following easy_install
 command:

  $ easy_install 'cdat_lite<4.3'
  
==========================================================================
""")


#------------------------------------------------------------------------------

setup(name='cdat_lite',
      description=description,
      long_description=long_description,
      version='%s%s' % (cdat_release, cdat_tag),
      url = CDAT_LITE_URL,
      download_url = NDG_EGG_REPOSITORY,
      maintainer = 'Stephen Pascoe',
      maintainer_email = 'Stephen.Pascoe@stfc.ac.uk',
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
      install_requires = ['setuptools>=0.6c1', 'numpy'],
      zip_safe = False,
      
      packages = find_packages('lib'),
      package_dir = {'': 'lib'},
      py_modules = ['cdat_info', 'MV2'],
      
      ext_modules = [
        makeExtension('cdtime'),
        makeExtension('unidata.udunits_wrap', 'unidata'),
        #!TODO: macro depends on whether NC4 is used
        makeExtension('cdms2.Cdunif', 'cdms2', macros=[('NONC4', None)]),
        Extension('cdms2._bindex',
                  ['Packages/cdms2/Src/_bindexmodule.c',
                   'Packages/cdms2/Src/bindex.c'],
                  ),
        makeExtension('genutil.array_indexing', 'genutil'),
        Extension('regrid2._regrid', ['Packages/regrid2/Src/_regridmodule.c']),
        Extension('regrid2._scrip', ['Packages/regrid2/Src/_scripmodule.c',
                                     'Packages/regrid2/Src/regrid.c']),
      ],

      # Since udunits.dat isn't in the Lib directory we use the data_files attribute
      # to install data.
      include_package_data = True,
      #package_data = {'cdat_lite.clib': ['include/*', 'lib/*']},
      data_files = [('unidata', ['Packages/unidata/Src/udunits.dat'])],
      
      entry_points = {
        'console_scripts': ['cdscan = cdat_lite.scripts:cdscan_main',
                            'cddump = cdat_lite.scripts:cddump_main',
                            'convertcdms = cdat_lite.scripts:convertcdms_main']
        },

      test_suite = 'nose.collector',
      
      cmdclass = {'build_ext': build_ext}
      )

    

