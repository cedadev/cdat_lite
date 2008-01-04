#!/usr/bin/env python
"""Support module for the cdat_lite setup.py script.


"""

#--------------------------------------------------------------------------------



import sys, os
from glob import glob

from setuptools import setup, Extension
from distutils.command.build_ext import build_ext as build_ext_orig
from distutils.cmd import Command


class ConfigError(Exception):
    """Configuration failed."""
    pass


def makeExtension(name, package_dir=None, sources=None,
                  include_dirs=None, library_dirs=None):
    """Convenience function for building extensions from the Packages directory.
    """

    if not package_dir:
        package_dir = name
    if not sources:
        sources = glob('Packages/%s/Src/*.c' % package_dir)
    if not include_dirs:
        include_dirs = ['Packages/%s/Include' % package_dir]
    if not library_dirs:
        library_dirs = ['Packages/%s/Lib' % package_dir]

    e = Extension(name, sources,
                  include_dirs=include_dirs,
                  library_dirs=library_dirs)

    return e


class build_ext(build_ext_orig):
    """
    Add distribution specific search paths and build libcdms first.
    """

    netcdf_version = '3.5.1'



    def finalize_options(self):
        """Append NetCDF and libcdms libraries and includes.
        """

        build_ext_orig.finalize_options(self)        

        # Non-option attributes used during run()
        self.build_base = self.distribution.command_obj['build'].build_base
        self.build_lib = self.distribution.command_obj['build'].build_lib

        self.netcdf_incdir, self.netcdf_libdir = self._findNetcdf()
        #self.netcdf_incdir = os.path.abspath('%s/netcdf-install/include' % self.build_base)
        #self.netcdf_libdir = os.path.abspath('%s/netcdf-install/lib' % self.build_base)

        # Option attributes
        self.include_dirs += [self.findNumericHeaders(), self.netcdf_incdir,
                              'libcdms/include']
        self.library_dirs += [self.netcdf_libdir, 'libcdms/lib']
        self.libraries += ['cdms', 'netcdf']

    def run(self):

        #self._buildNetcdf()
        self._buildLibcdms()

        build_ext_orig.run(self)

    def _findNetcdf(self):
        """Find NetCDF libraries installed on the system or prompt the user.

        Various heuristics are tried to find the NetCDF installation.
        """

        prefix = None
        inc_dir = None
        lib_dir = None

        def isPrefix(prefix):
            print ('Looking for NetCDF installation in %s ...' % prefix),
            if (os.path.exists('%s/lib/libnetcdf.a' % prefix) and 
                os.path.exists('%s/include/netcdf.h' % prefix)):
                print 'yes'
                return True
            else:
                print 'no'
                return False

        prefixes = ['/usr', '/usr/local', os.environ['HOME']]

        # Try finding a common NetCDF prefix
        for p in prefixes:
            if isPrefix(p):
                prefix = p
                break
        else:
            # Try looking for ncdump
            for ex_p in os.environ['PATH'].split(':'):
                if os.path.exists('%s/ncdump' % ex_p):
                    updir = os.path.dirname(ex_p.rstrip('/'))
                    if isPrefix(updir):
                        prefix = updir
                        break

        if not prefix:
            print '''===================================================
Please enter NetCDF installation prefix:''',
            prefix = raw_input()
            if not isPrefix(prefix):
                raise ValueError('Cannot find NetCDF libraries')

        return '%s/include' % prefix, '%s/lib' % prefix

    def _buildNetcdf(self):
        """Build the netcdf libraries."""
        if not os.path.exists('exsrc/netcdf-%s' % self.netcdf_version):
            self._system('cd exsrc; tar zxf netcdf.tar.gz')
        if not os.path.exists('exsrc/netcdf-%s/src/config.log' % self.netcdf_version):
            self._system('cd exsrc/netcdf-%s/src; CFLAGS=-fPIC ./configure --prefix=%s/netcdf-install' %
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

    def _buildLibcdms(self):
        """Build the libcdms library.
        """
        if os.path.exists('cdat_lite/clib/lib/libcdms.a'):
            return

        if not os.path.exists('libcdms/Makefile'):
            self._system('cd libcdms ; '
                         'CFLAGS="-fPIC" ./configure --disable-drs --disable-hdf --disable-dods '
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



    def findNumericHeaders(self):
        """We may or may not have the Numeric_headers module available.
        """

        try:
            import Numeric
        except ImportError:
            raise ConfigError, "Numeric is not installed."

        if Numeric.__version__ != '23.1':
            #!TODO only do this test on 64bit
            raise ConfigError("CDAT requires Numeric 23.1, version %s found" %
                              Numeric.__version__)

        if 'NUMERIC_INCLUDE' in os.environ:
            inc = os.environ['NUMERIC_INCLUDE']
            if os.path.exists(inc):
                return inc

        try:
            from Numeric_headers import get_numeric_include
            return get_numeric_include()
        except ImportError:
            pass

        sysinclude = sys.prefix+'/include/python%d.%d' % sys.version_info[:2]
        if os.path.exists(os.path.join(sysinclude, 'Numeric')):
            return sysinclude

        raise ConfigError, "Cannot find Numeric header files."
