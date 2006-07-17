#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py install --home=<home>

This script compiles libcdms.a and and a few essential CDAT packages
then installs them in I{<home>}.  cdms can then be accessed by adding
I{<home>/lib/python} to your python path.

"""

import sys, os

from distutils.core import setup, Distribution
from distutils.command.install import install
from distutils.command.build import build


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
         'List of packages to manage')
        ]

    def initialize_options(self):
        install.initialize_options(self)
        self.netcdf_prefix = None
        self.netcdf_include = None
        self.netcdf_lib = None
        self.cdat_packages = None

    def finalize_options(self):
        if not self.netcdf_prefix: self.netcdf_prefix = '/usr/local'
        if not self.netcdf_include:
            self.netcdf_include = self.netcdf_prefix + '/include'
        if not self.netcdf_lib:
            self.netcdf_lib = self.netcdf_prefix + '/lib'
        if not self.cdat_packages:
            self.cdat_packages = ','.join(['cdms', 'cdtime', 'cdutil',
                                           'genutil', 'regrid', 'Properties',
                                           'xmgrace', 'unidata'])

    def run(self):
        self.buildLibcdms()
        self.installPackages()

    
    def buildLibcdms(self):
        self._system('cd ../libcdms ; '
                     './configure --disable-drs --disable-hdf --disable-dods '
                     '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                     % (self.netcdf_include, self.netcdf_include,
                        self.netcdf_lib))
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

