#!/usr/bin/env python
"""Support module for the cdat_lite setup.py script.


"""

#--------------------------------------------------------------------------------



import sys, os
from glob import glob

from setuptools import setup, Extension
from distutils.command.build_ext import build_ext as build_ext_orig
from distutils.cmd import Command

import numpy

class ConfigError(Exception):
    """Configuration failed."""
    pass


def _findNetcdf():
    """Find NetCDF libraries installed on the system or prompt the user.
    
    Various heuristics are tried to find the NetCDF installation.
    """
    
    prefix = None
    inc_dir = None
    lib_dir = None

    def findLib(prefix):
        if prefix is None:
            return None
        libs = ['lib']
        if hasattr(sys, 'lib'):
            libs.append(sys.lib)

        for lib in libs:
            print 'Looking for NetCDF library in %s/%s ...' % (prefix, lib),
            if os.path.exists('%s/%s/libnetcdf.a' % (prefix, lib)):
                print 'yes'
                return '%s/%s' % (prefix, lib)
            else:
                print 'no'

    def findInclude(prefix):
        if prefix is None:
            return None
        print 'Looking for NetCDF include in %s/include ...' % prefix,
        if os.path.exists('%s/include/netcdf.h' % prefix):
            print 'yes'
            return '%s/include' % prefix
        else:
            print 'no'

    prefixes = ['/usr', '/usr/local',
                os.environ.get('HOME'), os.environ.get('NETCDF_HOME')]

    # Try finding a common NetCDF prefix
    found = False
    for p in prefixes:
        lib = findLib(p)
        include = findInclude(p)
        if lib and include:
            found = True
            break
    else:
        # Try looking for ncdump
        for ex_p in os.environ['PATH'].split(':'):
            if os.path.exists('%s/ncdump' % ex_p):
                updir = os.path.dirname(ex_p.rstrip('/'))
                lib = findLib(updir)
                include = findInclude(updir)
                if lib and include:
                    found = True
                    break

    if not found:
        print '''===================================================
NetCDF installation not found.
        
Please enter the NetCDF installation directory below or set the NETCDF_HOME
environment variable and re-run setup.py

Enter NetCDF installation prefix:''',
        prefix = raw_input()
        lib = findLib(prefix)
        include = findInclude(prefix)
        if not (lib and include):
            raise SystemExit

    return include, lib

netcdf_incdir, netcdf_libdir = _findNetcdf()



def makeExtension(name, package_dir=None, sources=None,
                  include_dirs=None, library_dirs=None):
    """Convenience function for building extensions from the Packages directory.
    """

    if include_dirs is None:
        include_dirs = []
    if library_dirs is None:
        library_dirs = []

    if not package_dir:
        package_dir = name
    if not sources:
        sources = glob('Packages/%s/Src/*.c' % package_dir)

    include_dirs += ['Packages/%s/Include' % package_dir, netcdf_incdir,
                     numpy.get_include()]
    library_dirs += ['Packages/%s/Lib' % package_dir, netcdf_libdir]

    e = Extension(name, sources,
                  include_dirs=include_dirs,
                  library_dirs=library_dirs)

    return e


class build_ext(build_ext_orig):
    """
    Add distribution specific search paths and build libcdms first.
    """


    def finalize_options(self):
        """Append NetCDF and libcdms libraries and includes.
        """

        build_ext_orig.finalize_options(self)        

        # Non-option attributes used during run()
        self.build_base = self.distribution.command_obj['build'].build_base
        self.build_lib = self.distribution.command_obj['build'].build_lib

        # Option attributes
        #self.include_dirs += [self.findNumericHeaders(), self.netcdf_incdir,
        #                      'libcdms/include']
        self.include_dirs += [numpy.get_include(), 'libcdms/include']
        self.library_dirs += [netcdf_libdir, 'libcdms/lib']
        self.libraries += ['cdms', 'netcdf']

    def run(self):

        self._buildLibcdms()

        build_ext_orig.run(self)

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
        #if os.path.exists('cdat_lite/clib/lib/libcdms.a'):
        #    return

        if not os.path.exists('libcdms/Makefile'):
            self._system('cd libcdms ; '
                         'CFLAGS="-fPIC" ./configure --disable-drs --disable-hdf --disable-dods '
                         '--disable-ql --with-ncinc=%s --with-ncincf=%s --with-nclib=%s'
                         % (netcdf_incdir, netcdf_incdir, netcdf_libdir))

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

        #if Numeric.__version__ != '23.1':
            #!TODO only do this test on 64bit
            #raise ConfigError("CDAT requires Numeric 23.1, version %s found" %
            #                  Numeric.__version__)
            

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
