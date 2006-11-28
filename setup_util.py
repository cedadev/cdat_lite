#!/usr/bin/env python
"""
Build minimal CDAT and install into a parallel directory.

usage: python setup.py install

This script compiles libcdms.a and and a few essential CDAT packages
then installs them.  If you want to install it locally to your home
directory use virtual_python.py.
"""

#--------------------------------------------------------------------------------



import sys, os

from distutils.command.build_ext import build_ext
from distutils.command.build import build

class ConfigError(Exception):
    """Configuration failed."""
    pass


class build_ext_withCdms(build_ext):

    netcdf_incdir = 'exsrc/netcdf-3.5.1/src/include'
    netcdf_libdir = 'exsrc/netcdf-3.5.1/src/lib'

    def finalize_options(self):

        build_ext.finalize_options(self)

        incdirs = [self._findNumericHeaders()]

        # Add numeric and netcdf header directories
        self.include_dirs = [self._findNumericHeaders(),
                             self.netcdf_incdir] + self.include_dirs
        self.library_dirs = [self.netcdf_libdir] + self.library_dirs


    def run(self):
        """Makes the egg binary distribution, ensuring libcdms is built first.
        """
        self._buildNetcdf()
        self._buildLibcdms()
        build_ext.run(self)

    def _buildNetcdf(self):
        """Build the netcdf libraries."""
        if not os.path.exists('exsrc/netcdf-3.5.1'):
            self._system('cd exsrc; tar zxf netcdf.tar.gz')
        if not os.path.exists('exsrc/netcdf-3.5.1/src/config.log'):
            self._system('cd exsrc/netcdf-3.5.1/src; LD_FLAGS=-fPIC ./configure')
        self._system('cd exsrc/netcdf-3.5.1/src; make')

        
    def _findNumericHeaders(self):
        """We may or may not have the Numeric_headers module available.
        """

        try:
            import Numeric
        except ImportError:
            raise ConfigError, "Numeric is not installed."
        
        try:
            from Numeric_headers import get_numeric_include
            return get_numeric_include()
        except ImportError:
            pass

        sysinclude = sys.prefix+'/include/python%d.%d' % sys.version_info[:2]
        if os.path.exists(os.path.join(sysinclude, 'Numeric')):
            return sysinclude
        
        raise ConfigError, "Cannot find Numeric header files."
        

    def _buildLibcdms(self):
        """Build the libcdms library.
        """
        if os.path.exists('libcdms/lib/libcdms.a'):
            return

        if not os.path.exists('libcdms/Makefile'):
            self._system('cd libcdms ; '
                         'CFLAGS=-fPIC ./configure --disable-drs --disable-hdf --disable-dods '
                         '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                         % (self.netcdf_incdir, self.netcdf_incdir, self.netcdf_libdir))

        self._system('cd libcdms ; make db_util ; make cdunif')

        
    def _system(self, cmd):
        """Like os.system but uses self.spawn() and therefore respects the
        --dry-run flag and aborts on failure.
        """
        self.spawn(['sh', '-c', cmd])

