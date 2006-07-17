#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py prefix

This script compiles libcdms.a and and a few essential CDAT packages then
installs them in I{prefix}.  cdms can then be accessed by adding I{prefix} to
your python path.

"""

#############################################################################
# Edit these to fit.
netcdf_libdir = '/usr/local/lib'
netcdf_incdir = '/usr/local/include'

# Which packages do you want to include
packages = ['cdms', 'cdtime', 'cdutil', 'genutil', 'regrid', 'Properties', 'xmgrace', 'unidata']
#############################################################################

import sys, os
from glob import glob

prefix = sys.argv[-1]


def do_cmd(cmd):
    print cmd
    if os.system(cmd) != 0:
        raise RuntimeError, 'Command failed'

# Configure libcdms
do_cmd('cd ../libcdms ; '
       './configure --prefix=%s --disable-drs --disable-hdf --disable-dods '
       '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
        % (prefix, netcdf_incdir, netcdf_incdir, netcdf_libdir))

# compile libcdms
do_cmd('cd ../libcdms ; make db_util ; make cdunif')

# Build each package
sys.argv = ['setup.py', 'build']
for package in packages:
    if package == 'unidata':
        # Unfortunately unidata assumes it's being installed in the default
        # path and tries to install the udunits data file there.
        do_cmd('cd ../Packages/%s ;'
               'PYTHONPATH=%s python ../../mini-install/unidata_setup.py '
               'install --home=%s'
               % (package, os.path.abspath('.'), prefix))
    else:
        do_cmd('cd ../Packages/%s ;'
               'PYTHONPATH=%s python setup.py install --home=%s'
               % (package, os.path.abspath('.'), prefix))


print '''
Success.

Now just add %s/lib/python to your PYTHONPATH to access cdms.
''' % prefix
