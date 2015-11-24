#!/usr/bin/env python
"""Support module for the cdat_lite setup.py script.


"""


import sys, os, shutil
from glob import glob
import subprocess as S

from setuptools import setup, Extension
from distutils.command.build_ext import build_ext as build_ext_orig
from distutils.cmd import Command
import distutils.ccompiler

import warnings

#--------------------------------------------------------------------------------

# Previous versions of cdat_lite used the NETCDF_HOME variable.  netcdf4-python uses NETCDF4_DIR.
# This supports both options
NETCDF_ENV_VARS = ['NETCDF_HOME', 'NETCDF4_DIR']
HDF5_ENV_VARS = ['HDF5_HOME', 'HDF5_DIR']


#--------------------------------------------------------------------------------


class ConfigException(Exception):
    pass

#
# Numpy detection code.  We want to be able to run commands like
# setup.py sdist without needing numpy installed.
#
try:
    import numpy
    has_numpy = True
except:
    has_numpy = False
    raise SystemExit("""
==========================================================================
numpy not available.  cdat_lite requires numpy to be installed first.  

It is recommended to install numpy by downloading the source and running
'python setup.py install'.  Easy_install is unreliable with this package.

==========================================================================
""")

def get_numpy_include():
    return os.path.abspath(numpy.get_include())


class DepFinder(object):
    """
    Find dependent libraries by looking in <prefix>/lib and <prefix>/include.

    """

    def __init__(self, depname, prefixes, includefile, libfile):

        self.depname = depname
        self.prefixes = prefixes + ['/usr', '/usr/local',
                                    os.environ.get('HOME')]
        self.includefile = includefile
        self.libfile = libfile

    def findLib(self, prefix):
        if prefix is None:
            return None
        libs = ['lib', 'lib64']
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
        
Please see README for instructions on detecting dependencies

'''
            raise SystemExit
        else:
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




def makeExtension(name, package_dir=None, sources=None,
                  include_dirs=None, library_dirs=None, macros=None):
    """Convenience function for building extensions from the Packages directory.
    """

    if include_dirs is None:
        numpy_inc = get_numpy_include()
        if numpy_inc:
            include_dirs = [numpy_inc]
        else:
            include_dirs = []
    if library_dirs is None:
        library_dirs = []

    if not package_dir:
        package_dir = name
    if not sources:
        sources = glob('Packages/%s/Src/*.c' % package_dir)

    include_dirs += [os.path.abspath(x) 
                     for x in ['Packages/%s/Include' % package_dir] + 
                              netcdf_config.include_dirs
                     ]
    library_dirs += [os.path.abspath(x) 
                     for x in ['Packages/%s/Lib' % package_dir] + 
                              netcdf_config.library_dirs
                     ]
    
    if macros:
        define_macros = macros + netcdf_config.define_macros
    else:
        define_macros = netcdf_config.define_macros

    # Remove any files or directories that don't exist
    include_dirs = [x for x in include_dirs if os.path.exists(x)]
    library_dirs = [x for x in library_dirs if os.path.exists(x)]

    libraries = netcdf_config.libraries

    # To force recompilation of extensions every time say it depends on
    # libcdms/config.status.  Problems with link conflicts when switching
    # between netcdf libraries suggest this might be necessary.
    depends = ['libcdms/config.status']

    e = Extension(name, sources,
                  libraries=libraries,
                  include_dirs=include_dirs,
                  library_dirs=library_dirs,
                  define_macros=define_macros,
                  depends=depends)

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
            if os.path.lexists(linkpath):
                os.remove(linkpath)
            os.symlink(os.path.abspath(mod),
                       linkpath)

    for package, dir in packageRoots.items():
        if package:
            sdir = os.path.join(root,package)
            if os.path.lexists(sdir):
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
        numpy_inc = get_numpy_include()
        if numpy_inc:
            self.include_dirs += [numpy_inc]
        self.include_dirs += [os.path.abspath('libcdms/include')] + netcdf_config.include_dirs
        self.library_dirs += netcdf_config.library_dirs + [os.path.abspath('libcdms/lib')]

        self.libraries += ['cdms'] + netcdf_config.libraries


    def run(self):

        self._buildLibcdms()

        build_ext_orig.run(self)

    def _linkFiles(self, files, destDir):
        for file in files:
            dest = os.path.abspath(os.path.join(destDir, os.path.basename(file)))
            src = os.path.abspath(file)            
            if os.path.lexists(dest):
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
        if netcdf_config.with_netcdf4:
            nc4_defs = '--with-hdf5inc=%s --with-hdf5lib=%s' % (
                netcdf_config.hdf5_incdir, netcdf_config.hdf5_libdir)
        else:
            nc4_defs = ''

        self._system('cd libcdms ; '
                     'CFLAGS="-fPIC" '
                     'CC=%(cc)s '
                     'sh ./configure --disable-drs --disable-hdf '
                     '--disable-ql --with-ncinc=%(ncinc)s --with-ncincf=%(ncinc)s --with-nclib=%(nclib)s %(nc4)s'
                     % dict(ncinc=netcdf_config.netcdf_incdir, nclib=netcdf_config.netcdf_libdir,
                            cc=cc, nc4=nc4_defs))
        
        self._system('cd libcdms ; make db_util ; make cdunif')

        
    def _system(self, cmd):
        """Like os.system but uses self.spawn() and therefore respects the
        --dry-run flag and aborts on failure.
        """
        self.spawn(['sh', '-c', cmd])



class NetCDFConfig(object):
    netcdf_incdir = None
    netcdf_libdir = None
    with_netcdf4 = None
    hdf5_incdir = None
    hdf5_libdir = None
    library_dirs = []
    libraries = []
    include_dirs = []
    define_macros = []

    def __init__(self):
        self.detect_ncconfig()
        self.config_netcdf()
        self.print_report()

    def print_report(self):
        print '''\
=================================================================
NetCDF configuration detection results
-----------------------------------------------------------------

  include-directories: %s
  library-directories: %s
  libraries:           %s
  netcdf-include-dir:  %s
  netcdf-library-dir:  %s
''' % (' '.join(self.include_dirs), 
       ' '.join(self.library_dirs),
       ' '.join(self.libraries), 
       self.netcdf_incdir, 
       self.netcdf_libdir,
       )
        if self.with_netcdf4:
            print '''\
  has-netcdf4:         Yes
  hdf5-include-dir:    %s
  hdf5-library-dir:    %s''' %  (self.hdf5_incdir, self.hdf5_libdir)
        else:
            print '''\
  has-netcdf4:         No
'''
        print '''\
=================================================================
'''    

    def detect_ncconfig(self):
        # Detect nc-config
        print 'Looking for nc-config ... ',
        rc = S.call('which nc-config', shell=True, stderr=None, stdout=S.PIPE)
        if rc == 0:
            print 'yes'
            self._has_ncconfig = True
        else:
            print 'no'
            self._has_ncconfig = False

    def config_netcdf(self):
        if self._has_ncconfig:
            self.ncconfig_includes()
            self.ncconfig_libs()
            self.ncconfig_nc4()

        else:
            prefixes = [os.environ.get(x) for x in NETCDF_ENV_VARS if x]
            self.netcdf_incdir, self.netcdf_libdir = DepFinder('NetCDF', prefixes,
                                                               includefile='netcdf.h',
                                                               libfile='libnetcdf.a').find()

            # If using NetCDF4 find the HDF5 libraries
            if check_ifnetcdf4(self.netcdf_incdir):
                prefixes = [os.environ.get(x) for x in HDF5_ENV_VARS if x]
                self.hdf5_incdir, self.hdf5_libdir = DepFinder('HDF5', prefixes,
                                                               includefile='hdf5.h', libfile='libhdf5.a').find()
                self.with_netcdf4 = True
            else:
                self.hdf5_incdir = False
                self.with_netcdf4 = False

    def ncconfig_nc4(self):
        has_nc4 = self.run_ncconfig('--has-nc4')[0]
        if 'yes' in has_nc4:
            self.with_netcdf4 = True
        else:
            self.with_netcdf4 = False

    def ncconfig_libs(self):
        """
        distutils and libcdms needs info in a different form to nc-config.
        This function mines for it.
        
        """
        libs = self.run_ncconfig('--libs')[0].split()
        for lib in libs:
            if lib[:2] == '-L':
                self.library_dirs.append(lib[2:])
            elif lib[:2] == '-l':
                self.libraries.append(lib[2:])
            else:
                raise Exception("Unrecognised nc-config library option: %s" % lib)

        # Now detect netcdf_libdir and hdf5_libdir
        for path in self.library_dirs:
            if glob(os.path.join(path, 'libnetcdf.*')):
                self.netcdf_libdir = path
            if glob(os.path.join(path, 'libhdf5.*')):
                self.hdf5_libdir = path


    def ncconfig_includes(self):
        """
        As ncconfig_libs but for includes

        """

        incs = self.run_ncconfig('--cflags')[0].split()
        for inc in incs:
            if inc[:2] == '-I':
                self.include_dirs.append(inc[2:])
            elif inc[:2] == '-D':
                macro = inc[2:]
                value = None
                if '=' in macro:
                    macro, value = macro.split('=')
                self.define_macros.append((macro, value))
            else:
                warings.warn("Unrecognised nc-config cflag %s" % inc)
            
        # Now detect netcdf_incdir and hdf5_incdir
        for path in self.include_dirs:
            if os.path.exists(os.path.join(path, 'netcdf.h')):
                self.netcdf_incdir = path
            if os.path.exists(os.path.join(path, 'hdf5.h')):
                self.hdf5_incdir = path
        


    def run_ncconfig(self, args):
        p = S.Popen('nc-config %s' % args, shell=True,
                    stdout=S.PIPE, stderr=S.PIPE, close_fds=True)
        if p.wait() != 0:
            raise ConfigException('nc-config failed: %s' % p.stderr.read().strip())

        return [x.strip() for x in p.stdout]




# bootstrap module
netcdf_config = NetCDFConfig()
