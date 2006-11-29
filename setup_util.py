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
from glob import glob

from distutils.command.build_ext import build_ext
from distutils.command.build import build

class ConfigError(Exception):
    """Configuration failed."""
    pass


class build_ext_withCdms(build_ext):

    netcdf_version = '3.5.1'

    def finalize_options(self):

        build_ext.finalize_options(self)

        incdirs = [self._findNumericHeaders()]

        # Add numeric and netcdf header directories
        self.include_dirs = [self._findNumericHeaders(), '%s/cdat_clib/include' % self.build_lib] + self.include_dirs
        self.library_dirs = ['%s/cdat_clib/lib' % self.build_lib] + self.library_dirs


    def run(self):
        """Makes the egg binary distribution, ensuring libcdms is built first.
        """
        self._buildNetcdf()
        self._buildLibcdms()
        build_ext.run(self)

    def _buildNetcdf(self):
        """Build the netcdf libraries."""
        if not os.path.exists('exsrc/netcdf-%s' % self.netcdf_version):
            self._system('cd exsrc; tar zxf netcdf.tar.gz')
        if not os.path.exists('exsrc/netcdf-%s/src/config.log' % self.netcdf_version):
            self._system('cd exsrc/netcdf-%s/src; LD_FLAGS=-fPIC ./configure --prefix=%s/exsrc/netcdf-install' % (self.netcdf_version, os.getcwd()))
        if not os.path.exists('exsrc/netcdf-install'):
            os.mkdir('exsrc/netcdf-install')
        self._system('cd exsrc/netcdf-%s/src; make install' % self.netcdf_version)

        if self.dry_run:
            return

        # Link the headers and libraries into the cdat_clib package
        os.mkdir('%s/cdat_clib/include' % self.build_lib)
        os.mkdir('%s/cdat_clib/lib' % self.build_lib)
        self._linkFiles(glob('exsrc/netcdf-install/include/*'),
                        '%s/cdat_clib/include' % self.build_lib)
        self._linkFiles(glob('exsrc/netcdf-install/lib/*'),
                        '%s/cdat_clib/lib' % self.build_lib)
 
    def _linkFiles(self, files, destDir):
        for file in files:
            dest = os.path.abspath(os.path.join(destDir, os.path.basename(file)))
            src = os.path.abspath(file)            
            if os.path.exists(dest):
                os.remove(dest)
            os.symlink(src, dest)
        
        
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
        if os.path.exists('cdat_clib/lib/libcdms.a'):
            return

        if not os.path.exists('libcdms/Makefile'):
            self._system('cd libcdms ; '
                         'CFLAGS=-fPIC ./configure --disable-drs --disable-hdf --disable-dods '
                         '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                         % (self.netcdf_incdir, self.netcdf_incdir, self.netcdf_libdir))

        self._system('cd libcdms ; make db_util ; make cdunif')

        # link into cdat_clib package
        self._linkFiles(glob('libcdms/include/*.h'), 'cdat_clib/include')
        self._linkFiles(glob('libcdms/lib/lib*.a'), 'cdat_clib/lib')
        

        
    def _system(self, cmd):
        """Like os.system but uses self.spawn() and therefore respects the
        --dry-run flag and aborts on failure.
        """
        self.spawn(['sh', '-c', cmd])

