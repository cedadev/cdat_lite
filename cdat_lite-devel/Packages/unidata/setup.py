from numpy.distutils.core import setup, Extension
import os,sys,string

target_prefix = sys.prefix
for i in range(len(sys.argv)):
    a = sys.argv[i]
    if a=='--prefix':
        target_prefix=sys.argv[i+1]
    sp = a.split("--prefix=")
    if len(sp)==2:
        target_prefix=sp[1]

setup (name = "udunits",
       version='1.0',
       author='doutriaux1@llnl.gov',
       description = "Python wrapping for UDUNITS package developped by UNIDATA",
       url = "http://www-pcmdi.llnl.gov/software",
       packages = ['unidata'],
       package_dir = {'unidata': 'Lib'},
       ext_modules = [
    Extension('unidata.udunits_wrap',
              ['Src/udunits_wrap.c',
               'Src/utparse.c',
               'Src/utlib.c',
               'Src/utscan.c',
               ],
              include_dirs = ['Include']
              )
    ]
      )

f=open('Src/udunits.dat')
version=sys.version.split()[0].split('.')
version=string.join(version[:2],'.')
try:
    f2=open(target_prefix+'/lib/python'+version+'/site-packages/unidata/udunits.dat','w')
except:
    f2=open(target_prefix+'/lib64/python'+version+'/site-packages/unidata/udunits.dat','w')
    
for l in f.xreadlines():
    f2.write(l)
f2.close()
