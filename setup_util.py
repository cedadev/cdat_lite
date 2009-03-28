#!/usr/bin/env python
"""Support module for the cdat_lite setup.py script.


"""

#--------------------------------------------------------------------------------



import sys, os, shutil
from glob import glob

from setuptools import setup, Extension
from distutils.command.build_ext import build_ext as build_ext_orig
from distutils.cmd import Command
import distutils.ccompiler

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

    prefixes = [os.environ.get('NETCDF_HOME'), '/usr', '/usr/local',
                os.environ.get('HOME')]

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




def check_ifnetcdf4(netcdf4_incdir):
    """
    Check whether NetCDF4 is installed.

    Code borrowed from the python netcdf4 bindings
    http://netcdf4-python.googlecode.com

    This will only return True if netcdf4_incdir points to a NetCDF4
    library compiled with --enable-netcdf-4

    """
    try:
        f = open(os.path.join(netcdf4_incdir,'netcdf.h'))
    except IOError:
        return False
    isnetcdf4 = False
    for line in f:
        if line.startswith('nc_inq_compound'):
            isnetcdf4 = True
    return isnetcdf4



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



def buildLibTree(packageRoots, mods=None, root='./lib'):
    """
    Symbolically link the contents of each package directory to a common root.

    This is required to support develop eggs which only works from a single
    directory root.

    @warning: The root will be removed before being reconstructed.
    
    """

    if os.path.exists(root):
        shutil.rmtree(root)
    os.mkdir(root)

    if mods:
        for mod in mods:
            os.symlink(os.path.abspath(mod),
                       os.path.join(root, os.path.basename(mod)))

    for package, dir in packageRoots.items():
        if package:
            os.mkdir(os.path.join(root, package))
        for f in os.listdir(dir):
            p = os.path.abspath(os.path.join(dir, f))
            os.symlink(p, os.path.join(root, package, f))
    

class build_ext(build_ext_orig):
    """
    Add distribution specific search paths and build libcdms first.
    """


    def finalize_options(self):
        """Append NetCDF and libcdms libraries and includes.
        """

        build_ext_orig.finalize_options(self)        

        # Non-option attributes used during run()
        #self.build_base = self.distribution.command_obj['build'].build_base
        #self.build_lib = self.distribution.command_obj['build'].build_lib

        # Option attributes
        #self.include_dirs += [self.findNumericHeaders(), self.netcdf_incdir,
        #                      'libcdms/include']
        self.include_dirs += [numpy.get_include(), 'libcdms/include']
        self.library_dirs += [netcdf_libdir, 'libcdms/lib']

        self.libraries += ['cdms', 'netcdf']

        # If NetCDF4 support add hdf5 libraries
        if check_ifnetcdf4(netcdf_incdir):
            print 'NetCDF4 detected.  Including HDF libraries'
            self.libraries += ['hdf5', 'hdf5_hl']

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

        if self.compiler:
            cc = self.compiler
        else:
            cc = distutils.ccompiler.new_compiler().compiler[0]

        # If NetCDF4 support we need to add HDF5 libraries in.
        # Also ./configure doesn't include the right libraries so add the
        # necessary declarations to CFLAGS too.
        if check_ifnetcdf4(netcdf_incdir):
            'NetCDF4 detected.  Configuring libcdms with NetCDF4 support'
            nc4_defs = '-I%(ncinc)s -L%(nclib)s -lnetcdf -lhdf5 -lhdf5_hl' % dict(
                ncinc=netcdf_incdir, nclib=netcdf_libdir)
        else:
            nc4_defs = ''

        if not os.path.exists('libcdms/Makefile'):
            self._system('cd libcdms ; '
                         'CFLAGS="-fPIC %(nc4)s" '
                         'CC=%(cc)s '
                         ' ./configure --disable-drs --disable-hdf --enable-dap '
                         '--disable-ql --with-ncinc=%(ncinc)s --with-ncincf=%(ncinc)s --with-nclib=%(nclib)s'
                         % dict(ncinc=netcdf_incdir, nclib=netcdf_libdir,
                                cc=cc, nc4=nc4_defs))
        
        self._system('cd libcdms ; make db_util ; make cdunif')

        #!DEPRECATED: No need to include libcdms.a in the egg
        # link into cdat.clib package
        #self._linkFiles(glob('libcdms/include/*.h'), '%s/cdat_lite/clib/include' % self.build_lib)
        #self._linkFiles(glob('libcdms/lib/lib*.a'), '%s/cdat_lite/clib/lib' % self.build_lib)
        

        
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
