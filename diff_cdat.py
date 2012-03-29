#!/usr/bin/env python
"""
Run diff to compare cdat_lite source with a full CDAT source tree.

usage: diff_cdat.py <CDAT_SRC_PATH> [<TAG>]

"""

import sys, os, subprocess

packages = ['cdms2', 'cdutil', 'ncml', 'regrid2', 'xmgrace',
            'cdtime', 'genutil', 'Properties', 'unidata']



def diff_package(pkg, name, cdat_path, exclude, tag=None):
    if tag is None:
        tagstr = ''
    else:
        tagstr = '-%s' % tag

    cdat_pkg = os.path.join(cdat_path, pkg)
    patch = '%s%s.patch' % (name, tagstr)
    exclude_args = reduce(list.__add__, (['-x', "'%s'" % x] for x in exclude))
    cmd = ['diff', '-Nru'] + exclude_args + [pkg, cdat_pkg]
    print ' '.join(cmd)
    p = subprocess.Popen(' '.join(cmd), stdout=subprocess.PIPE, shell=True)
    
    out = open(patch, 'w')
    for line in p.stdout:
        out.write(line)

def main(argv=sys.argv[1:]):
    cdat_path = argv[0]
    if len(argv) > 1:
        tag = argv[1]
    else:
        tag = None

    diff_package('libcdms', 'libcdms', cdat_path,
                 exclude=['.svn', 'config.*', 'cdunifpp*', 'Makefile'],
                 tag=tag)


    for pkg in packages:
        diff_package('Packages/%s' % pkg, pkg, cdat_path,
                     exclude=['.svn', 'build'],
                     tag=tag)

if __name__ == '__main__':
    main()
