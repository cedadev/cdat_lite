#!/usr/bin/env python
"""Build the cdat_lite distribution.
"""


import sys, os, shutil

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
cdat_release = '5.0'
cdat_tag = ''
cdunifpp_version = '0.13pre1'
cdat_lite_version = '0.2.9pre2'


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

def copyScripts(scripts=['cdscan', 'cddump']):
    """In order to put cdat scripts in their own package they are copied
    into the cdat/scripts directory.

    """
    for script in scripts:
        src = os.path.abspath(os.path.join('libcdms/src/python', script))
        dest = os.path.abspath(os.path.join('cdat_lite', 'scripts', script+'.py'))
        shutil.copy(src, dest)

    shutil.copy('Packages/cdms2/Script/convertcdms.py',
                os.path.abspath(os.path.join('cdat_lite', 'scripts')))
        
copyScripts()

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

### This is untested but I think it will be useful when we try installing
### on suse
##
## # Suse 10.0 has a bug that prevents numpy installing properly.  This test
## # catches the problem and advises a solution
## try:
##     import numpy
## except ImportError, e:
##     if 'undefined symbol:_gfortran_filename' in str(e):
##         raise SystemExit("""
## ==========================================================================
##  Your numpy installation is broken due to a known problem with libblas on
##  your system.

##  We recommend you install ATLAS (http://math-atlas.sourceforge.net) and
##  reinstall numpy with:

##  $ ATLAS=<atlas-home> easy_install -U numpy

##  You may need to remove your current installation of numpy first.
## ==========================================================================
## """)
##     else:
##         raise e
import numpy

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
      install_requires = ['setuptools>=0.6c1'],
      zip_safe = False,
      
      packages = ['unidata', 'cdms2', 'cdutil', 'xmgrace', 'genutil',
                  'PropertiedClasses', 'regrid2', 'kinds',
                  'cdat_lite', 'cdat_lite.clib', 'cdat_lite.scripts', 'cdat_lite.test'],
      py_modules = ['MV2'],
      package_dir = {'': 'Packages/cdms2',
                     'unidata': 'Packages/unidata/Lib',
                     'cdms2': 'Packages/cdms2/Lib',
                     'cdutil': 'Packages/cdutil/Lib',
                     'xmgrace': 'Packages/xmgrace/Lib',
                     'genutil': 'Packages/genutil/Lib',
                     'PropertiedClasses': 'Packages/Properties/Lib',
                     'regrid2': 'Packages/regrid2/Lib',
                     'kinds': 'Packages/kinds/Lib',
                     'cdat_lite': 'cdat_lite',
                     'cdat_lite.scripts': 'cdat_lite/scripts',
                     'cdat_lite.clib': 'cdat_lite/clib',
                     'cdat_lite.test': 'cdat_lite/test'
                     },
      
      ext_modules = [
        makeExtension('cdtime'),
        makeExtension('unidata.udunits_wrap', 'unidata'),
        makeExtension('cdms2.Cdunif', 'cdms2'),
        Extension('cdms2._bindex',
                  ['Packages/cdms2/Src/_bindexmodule.c',
                   'Packages/cdms2/Src/bindex.c'],
                  ),
        makeExtension('genutil.array_indexing', 'genutil'),
        Extension('regrid2._regrid', ['Packages/regrid2/Src/_regridmodule.c']),
        Extension('regrid2._scrip', ['Packages/regrid2/Src/_scripmodule.c',
                                     'Packages/regrid2/Src/regrid.c']),
        makeExtension('kinds._kinds', 'kinds'),
      ],

      # Since udunits.dat isn't in the Lib directory we use the data_files attribute
      # to install data.
      include_package_data = True,
      package_data = {'cdat_lite.clib': ['include/*', 'lib/*']},
      #package_data = {'unidata': ['Packages/unidata/Src/*.dat']},
      data_files = [('unidata', ['Packages/unidata/Src/udunits.dat'])],
      
      entry_points = {
        'console_scripts': ['cdscan = cdat_lite.scripts:cdscan_main',
                            'cddump = cdat_lite.scripts:cddump_main',
                            'convertcdms = cdat_lite.scripts:convertcdms_main']
        },

      test_suite = 'nose.collector',
      
      cmdclass = {'build_ext': build_ext}
      )

    

