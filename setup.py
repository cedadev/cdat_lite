#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py install

This script compiles libcdms.a and and a few essential CDAT packages
then installs them.  If you want to install it locally to your home
directory use virtual_python.py.
"""

import sys, os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Distribution
from setuptools.command.install import install
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
        ('cdat-dist=', None,
         'Location of your CDAT distribution'),
        ('cdat-packages=', None,
         'List of packages to manage')
        ]

    def initialize_options(self):
        install.initialize_options(self)
        self.netcdf_prefix = None
        self.netcdf_include = None
        self.netcdf_lib = None
        self.cdat_dist = None
        self.cdat_packages = None

    def finalize_options(self):
        if not self.netcdf_prefix: self.netcdf_prefix = '/usr/local'
        if not self.netcdf_include:
            self.netcdf_include = self.netcdf_prefix + '/include'
        if not self.netcdf_lib:
            self.netcdf_lib = self.netcdf_prefix + '/lib'
        if not self.cdat_dist:
            self.cdat_dist = '..'
        if not self.cdat_packages:
            self.cdat_packages = ','.join(['cdms', 'cdtime', 'cdutil',
                                           'genutil', 'regrid', 'Properties',
                                           'xmgrace', 'unidata'])

    def run(self):
        self.buildLibcdms()
        self.installPackages()

    
    def buildLibcdms(self):
        self._system('cd %s/libcdms ; '
                     './configure --disable-drs --disable-hdf --disable-dods '
                     '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                     % (self.cdat_dist, self.netcdf_include, self.netcdf_include,
                        self.netcdf_lib))
        self._system('cd %s/libcdms ; make db_util ; make cdunif'
                     % self.cdat_dist)

    def installPackages(self):
        curdir = os.path.abspath('.')
        for package in self.cdat_packages.split(','):
            self._system('cd %s/Packages/%s ;'
                         'PYTHONPATH=%s python setup.py install'
                         % (self.cdat_dist, package, curdir))

    def _system(self, cmd):
        self.execute(os.system, (cmd,))


setup(name = 'mini-cdat',
      cmdclass = {'install': MyInstall}
      )

