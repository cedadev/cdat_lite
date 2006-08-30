#!/usr/bin/env python
"""
A fairly rough and ready script for creating an egg of distutils.  This
is usefull for using eggs on python installations that don't have the
devel part of python installed.
"""

import sys, os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
import distutils

# Make a local copy of distutils
import tempfile

tmpdir = tempfile.mkdtemp()
print "Creating temporary directory %s" % tmpdir
os.system('cp -R %s %s' % (distutils.__path__[0], tmpdir))

setup(name='distutils',
      description=distutils.__doc__,
      version = distutils.__version__,
      url = 'http://www.python.org',
      packages = ['distutils', 'distutils.command'],
      package_dir = {'': tmpdir}
      )

print "Removing temporary directory %s" % tmpdir
os.system('rm -r %s' % tmpdir)
