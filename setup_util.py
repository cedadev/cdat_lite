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



class DepFinder(object):
    """
    Find dependent libraries by looking in <prefix>/lib and <prefix>/include.

    """

    def __init__(self, depname, homeenv, includefile, libfile):
        self.depname = depname
        self.homeenv = homeenv
        self.prefixes = [os.environ.get(homeenv), '/usr', '/usr/local',
                os.environ.get('HOME')]
        self.includefile = includefile
        self.libfile = libfile

    def findLib(self, prefix):
        if prefix is None:
            return None
        libs = ['lib']
        if hasattr(sys, 'lib'):
            libs.append(sys.lib)

        for lib in libs:
            print 'Looking for %s library in %s/%s ...' % (self.depname, prefix, lib),
            if os.path.exists('%s/%s/%s' % (prefix, lib, self.libfile)):
                print 'yes'
                return '%s/%s' % (prefix, lib)
            else:
                print 'no'

    def findInclude(self, prefix):
        if prefix is None:
            return None
        print 'Looking for %s include in %s/include ...' % (self.depname, prefix),
        if os.path.exists('%s/include/%s' % (prefix, self.includefile)):
            print 'yes'
            return '%s/include' % prefix
        else:
            print 'no'

    def find(self):
        # Try finding a common NetCDF prefix
        found = False
        for p in self.prefixes:
            lib = self.findLib(p)
            include = self.findInclude(p)
            if lib and include:
                found = True
                break

        if not found:
            print '''===================================================
%s installation not found.
        
Please enter the %s installation directory below or set the %s
environment variable and re-run setup.py

Enter %s installation prefix:''' % (self.depname, self.depname, self.homeenv, self.depname),
            prefix = raw_input()
            lib = self.findLib(prefix)
            include = self.findInclude(prefix)
            if not (lib and include):
                raise SystemExit

        return include, lib


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




netcdf_incdir, netcdf_libdir = DepFinder('NetCDF', 'NETCDF_HOME',
                                         includefile='netcdf.h',
                                         libfile='libnetcdf.a').find()
# If using NetCDF4 find the HDF5 libraries
if check_ifnetcdf4(netcdf_incdir):
    print 'NetCDF4 detected.  Including HDF libraries'
    hdf5_incdir, hdf5_libdir = DepFinder('HDF5', 'HDF5_HOME',
                                                 includefile='hdf5.h', libfile='libhdf5.a').find()
else:
    hdf5_incdir = False





def makeExtension(name, package_dir=None, sources=None,
                  include_dirs=None, library_dirs=None, macros=None):
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
                  library_dirs=library_dirs,
                  define_macros=macros)

    return e



def buildLibTree(packageRoots, mods=None, root='./lib'):
    """
    Symbolically link the contents of each package directory to a common root.

    This is required to support develop eggs which only works from a single
    directory root.

    @warning: The root will be removed before being reconstructed.
    
    """


    if mods:
        for mod in mods:
            modpath = os.path.abspath(mod)
            linkpath = os.path.join(root, os.path.basename(mod))
            if os.path.exists(linkpath):
                os.remove(linkpath)
            os.symlink(os.path.abspath(mod),
                       linkpath)

    for package, dir in packageRoots.items():
        if package:
            sdir = os.path.join(root,package)
            if os.path.exists(sdir):
                shutil.rmtree(sdir)
            os.mkdir(sdir)
        for f in os.listdir(dir):
            p = os.path.abspath(os.path.join(dir, f))
            os.symlink(p, os.path.join(root, package, f))
    


def copyScripts(scripts=['cdscan', 'cddump']):
    """In order to put cdat scripts in their own package they are copied
    into the cdat/scripts directory.

    """
    for script in scripts:
        src = os.path.abspath(os.path.join('Packages/cdms2/Script', script))
        if not os.path.exists(src):
            src = os.path.abspath(os.path.join('libcdms/src/python', script))
            
        dest = os.path.abspath(os.path.join('lib', 'cdat_lite', 'scripts', script+'.py'))
        shutil.copy(src, dest)

    shutil.copy('Packages/cdms2/Script/convertcdms.py',
                os.path.abspath(os.path.join('lib', 'cdat_lite', 'scripts')))
        


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
        self.include_dirs += [numpy.get_include(), 'libcdms/include']
        self.library_dirs += [netcdf_libdir, 'libcdms/lib']

        self.libraries += ['cdms', 'netcdf']

        # If NetCDF4 support add hdf5 libraries
        if hdf5_incdir:
            self.libraries += ['hdf5', 'hdf5_hl']
            self.library_dirs += [hdf5_libdir]

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
        if hdf5_incdir:
            nc4_defs = '--with-hdf5inc=%s --with-hdf5lib=%s' % (
                hdf5_incdir, hdf5_libdir)
        else:
            nc4_defs = ''

        self._system('cd libcdms ; '
                     'CFLAGS="-fPIC" '
                     'CC=%(cc)s '
                     ' ./configure --disable-drs --disable-hdf'
                     '--disable-ql --with-ncinc=%(ncinc)s --with-ncincf=%(ncinc)s --with-nclib=%(nclib)s %(nc4)s'
                     % dict(ncinc=netcdf_incdir, nclib=netcdf_libdir,
                            cc=cc, nc4=nc4_defs))
        
        self._system('cd libcdms ; make db_util ; make cdunif')

        
    def _system(self, cmd):
        """Like os.system but uses self.spawn() and therefore respects the
        --dry-run flag and aborts on failure.
        """
        self.spawn(['sh', '-c', cmd])



