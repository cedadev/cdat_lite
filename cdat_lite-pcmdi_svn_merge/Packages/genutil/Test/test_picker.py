#!/usr/bin/env python

import cdms,genutil,vcs,cdtime,os,sys
cdms.setAutoBounds('on')
#f=cdms.open('/pcmdi/obs/mo/ta/rnl_ncep/ta.rnl_ncep.ctl')
f=cdms.open(os.path.join(sys.prefix,'sample_data','ta_ncep_87-6-88-4.nc'))

s2=f('ta',slice(0,1))

print s2.shape
print s2.getLevel()[:]
print s2.getLevel().getBounds()[:4]

s=f('ta',slice(0,1),genutil.picker(level=[1000,700,800],match=0))

print s.shape
s.info()

x=vcs.init()
x.plot(s[0,-1])


s3=f('ta',genutil.picker(time=['1987-7','1988-1',cdtime.comptime(1988,3)],level=[1000,700,850]))

s3.info()
print s3.shape
print s3.getTime().asComponentTime()
print s3.getLevel()[:]
