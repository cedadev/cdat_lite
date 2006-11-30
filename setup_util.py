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

from distutils.command.build_ext import build_ext as build_ext_orig
from distutils.cmd import Command


class ConfigError(Exception):
    """Configuration failed."""
    pass


class build_ext(build_ext_orig):
    """
    Run subcommands first.
    """

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
        build_ext_orig.run(self)

    sub_commands = build_ext_orig.sub_commands + [('build_cdms', None)]


class build_cdms(Command):

    description = 'build libcdms'
    user_options = [
        ('build-base=', 'b',
         "base directory for build library"),
        ('build-lib=', None,
         "build directory for all distribution"),
        ]

    boolean_options = ['debug', 'force']
    
    netcdf_version = '3.5.1'

    def initialize_options(self):
        self.build_base = None
        self.build_lib = None
        self.debug = 0
        self.force = 0

    def finalize_options(self):

        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('build_lib', 'build_lib'),
                                   ('debug', 'debug'),
                                   ('force', 'force'))

        # Add numeric and netcdf header directories
        self.netcdf_incdir = '%s/netcdf-install/include' % self.build_base
        self.netcdf_libdir = '%s/netcdf-install/lib' % self.build_base
        self.include_dirs = [self._findNumericHeaders(), self.netcdf_incdir]
        self.library_dirs = [self.netcdf_libdir]


    def run(self):
        self._buildNetcdf()
        self._buildLibcdms()

    def _buildNetcdf(self):
        """Build the netcdf libraries."""
        if not os.path.exists('exsrc/netcdf-%s' % self.netcdf_version):
            self._system('cd exsrc; tar zxf netcdf.tar.gz')
        if not os.path.exists('exsrc/netcdf-%s/src/config.log' % self.netcdf_version):
            self._system('cd exsrc/netcdf-%s/src; LD_FLAGS=-fPIC ./configure --prefix=%s/netcdf-install' %
                         (self.netcdf_version, os.path.abspath(self.build_base)))
        if not os.path.exists('%s/netcdf-install' % self.build_base):
            os.mkdir('%s/netcdf-install' % self.build_base)
        self._system('cd exsrc/netcdf-%s/src; make install' % (self.netcdf_version))

        if self.dry_run:
            return

        # Link the headers and libraries into the cdat.clib package
        self._linkFiles(glob('%s/netcdf-install/include/*' % self.build_base),
                        '%s/cdat_lite/clib/include' % self.build_lib)
        self._linkFiles(glob('%s/netcdf-install/lib/*' % self.build_base),
                        '%s/cdat_lite/clib/lib' % self.build_lib)
 
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
        if os.path.exists('cdat_lite/clib/lib/libcdms.a'):
            return

        if not os.path.exists('libcdms/Makefile'):
            self._system('cd libcdms ; '
                         'CFLAGS=-fPIC ./configure --disable-drs --disable-hdf --disable-dods '
                         '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                         % (self.netcdf_incdir, self.netcdf_incdir, self.netcdf_libdir))

        self._system('cd libcdms ; make db_util ; make cdunif')

        # link into cdat.clib package
        self._linkFiles(glob('libcdms/include/*.h'), '%s/cdat_lite/clib/include' % self.build_lib)
        self._linkFiles(glob('libcdms/lib/lib*.a'), '%s/cdat_lite/clib/lib' % self.build_lib)
        

        
    def _system(self, cmd):
        """Like os.system but uses self.spawn() and therefore respects the
        --dry-run flag and aborts on failure.
        """
        self.spawn(['sh', '-c', cmd])

