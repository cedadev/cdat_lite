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


class MyBuild(build):
    """Building multiple different distributions from the same directory
    doesn't work with standard distutils or setuptools because the distribution's state
    is stored in the build directory.  This class tries to fix the problem, although
    it may not work with more advanced setuptools features.
    """

    def initialize_options(self):
        build.initialize_options(self)

        # Make build_base distribution-specific.
        self.build_base = '%s-%s' % (self.build_base, self.distribution.metadata.name)

class MyBuild_ext(build_ext):

    user_options = [
        ('netcdf-incdir=', None,
         'directory containing netcdf.h (overrides --netcdf-prefix)'),
        ('netcdf-libdir=', None,
         'directory containing libnetcdf.a (overrides --netcdf-prefix)'),
        ('netcdf-prefix=', None,
         'location of your netcdf installation')
        ] + build_ext.user_options

    def initialize_options(self):
        build_ext.initialize_options(self)

        self.netcdf_incdir = None
        self.netcdf_libdir = None
        self.netcdf_prefix = None

    def finalize_options(self):

        build_ext.finalize_options(self)

        from Numeric_headers import get_numeric_include
        incdirs = [get_numeric_include()]

        # We try to allow netcdf.h and libnetcdf.a to be detected automatically
        # or with command-line options here.
        if not self.netcdf_incdir and self.netcdf_prefix:
            self.netcdf_incdir = os.path.join(self.netcdf_prefix, 'include')
        if not self.netcdf_libdir and self.netcdf_prefix:
            self.netcdf_libdir = os.path.join(self.netcdf_prefix, 'lib')

        if self.netcdf_incdir:
            incdirs.append(self.netcdf_incdir)

        # prepend numeric and netcdf header directories
        self.include_dirs = incdirs + self.include_dirs

        if self.netcdf_libdir:
            self.library_dirs = [self.netcdf_libdir] + self.library_dirs

        # Finally re-scan self.*_dirs for the location of the netcdf files.
        # This covers the case when --netcdf-* hasn't been set but they are
        # in standard locations.
        (self.netcdf_incdir, self.netcdf_libdir) = self._findNetcdfDirs()

    def run(self):
        """Makes the egg binary distribution, ensuring libcdms is built first.
        """
        self._buildLibcdms()
        build_ext.run(self)

    def _findNetcdfDirs(self):
        """We expect to find netcdf.h on self.include_dirs and libnetcdf.a on
        self.library_dirs.

        @return: (netcdf_include_dir, netcdf_library_dir)
        """

        incpath = None
        libpath = None

        for dir in self.include_dirs + ['/usr/include', '/usr/local/include']:
            if os.path.exists(os.path.join(dir, "netcdf.h")):
                incpath = dir
                break
        else:
            raise ConfigError, ("Cannot find your netcdf headers.  "
                                "Please set --netcdf-incdir or --netcdf-prefix")

        for dir in self.library_dirs + ['/usr/lib', '/usr/local/lib']:
            if os.path.exists(os.path.join(dir, "libnetcdf.a")):
                libpath = dir
                break
        else:
            raise ConfigError, ("Cannot find your netcdf libraries.  "
                                "Please set --netcdf-incdir or --netcdf-prefix")

        return (incpath, libpath)


    def _buildLibcdms(self):
        """Build the libcdms library.

        @param netcdf_include: the directory containing netcdf.h
        @param netcdf_lib: the directory containing libnetcdf.a
        """
        if os.path.exists('libcdms/lib/libcdms.a'):
            return

        if not os.path.exists('libcdms/Makefile'):
            netcdf_include, netcdf_lib = self._findNetcdfDirs()
            self._system('cd libcdms ; '
                         'CFLAGS=-fPIC ./configure --disable-drs --disable-hdf --disable-dods '
                         '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                         % (netcdf_include, netcdf_include, netcdf_lib))

        self._system('cd libcdms ; make db_util ; make cdunif')

        
    def _system(self, cmd):
        """Like os.system but uses self.spawn() and therefore respects the
        --dry-run flag and aborts on failure.
        """
        self.spawn(['sh', '-c', cmd])

