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

from distutils.core import setup
from distutils.command.install import install

prefix = sys.argv[-1]


def do_cmd(cmd):
    print cmd
    if os.system(cmd) != 0:
        raise RuntimeError, 'Command failed'


class MyInstall(install):

    description = "Install minimal CDAT"

    user_options = install.user_options + [
        ('netcdf-prefix=', None,
         'Location of your netcdf distribution'),
        ('netcdf-include=', None,
         'Location of your netcdf include directory.  Overrides --netcdf-prefix'),
        ('netcdf-lib=', None,
         'Location of your netcdf lib directory.  Overrides --netcdf-prefix'),
        ('cdat-packages=', None,
         'List of packages to install')
        ]

    def initialize_options(self):
        install.initialize_options(self)
        self.netcdf_prefix = None
        self.netcdf_include = None
        self.netcdf_lib = None
        self.cdat_packages = 'cdms,cdtime,cdutil,genutil,regrid,Properties,xmgrace,unidata'

    def run(self):
        self.buildLibcdms()
        self.installPackages()

        print '''
Success.

Now just add %s/lib/python to your PYTHONPATH to access cdms.
''' % self.home

    
    def buildLibcdms(self):
        if self.netcdf_prefix:
            netcdf_incdir = '%s/include' % self.netcdf_prefix
            netcdf_libdir = '%s/lib' % self.netcdf_prefix
        else:
            netcdf_incdir = '/usr/local/include'
            netcdf_libdir = '/usr/local/lib'
        if self.netcdf_include:
            netcdf_incdir = self.netcdf_include
        if self.netcdf_lib:
            netcdf_libdir = self.netcdf_lib

        self._system('cd ../libcdms ; '
                     './configure --disable-drs --disable-hdf --disable-dods '
                     '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                     % (netcdf_incdir, netcdf_incdir, netcdf_libdir))
        self._system('cd ../libcdms ; make db_util ; make cdunif')

    def installPackages(self):
        curdir = os.path.abspath('.')
        for package in self.cdat_packages.split(','):
            if package == 'unidata':
                # Unfortunately unidata assumes it's being installed in the default
                # path and tries to install the udunits data file there.
                self._system('cd ../Packages/%s ;'
                             'PYTHONPATH=%s python ../../mini-install/unidata_setup.py '
                             'install --home=%s'
                             % (package, curdir, self.home))
            else:
                self._system('cd ../Packages/%s ;'
                             'PYTHONPATH=%s python setup.py install --home=%s'
                             % (package, curdir, self.home))

    def _system(self, cmd):
        self.execute(os.system, (cmd,))





setup(name = 'mini-cdat',
      cmdclass = {'install': MyInstall}
      )


raise SystemExit

# Install each package
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
