#!/usr/bin/env python
"""
Run diff to compare cdat_lite source with a full CDAT source tree.

usage: diff_cdat.py <CDAT_SRC_PATH>

"""

import sys, os, subprocess

packages = ['cdms2', 'cdutil', 'ncml', 'regrid2', 'xmgrace',
            'cdtime', 'genutil', 'Properties', 'unidata']



def diff_package(pkg, name, cdat_path, exclude):
    cdat_pkg = os.path.join(cdat_path, pkg)
    patch = '%s.patch' % name
    exclude_args = reduce(list.__add__, (['-x', "'%s'" % x] for x in exclude))
    cmd = ['diff', '-ru'] + exclude_args + [pkg, cdat_pkg]
    print ' '.join(cmd)
    p = subprocess.Popen(' '.join(cmd), stdout=subprocess.PIPE, shell=True)
    
    out = open(patch, 'w')
    for line in p.stdout:
        out.write(line)

def main(argv=sys.argv[1:]):
    (cdat_path, ) = argv

    diff_package('libcdms', 'libcdms', cdat_path,
                 exclude=['.svn', 'config.*', 'cdunifpp*', 'Makefile'])


    for pkg in packages:
        diff_package('Packages/%s' % pkg, pkg, cdat_path,
                     exclude=['.svn', 'build'])

if __name__ == '__main__':
    main()
