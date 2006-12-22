#!/usr/bin/env python

import cdms,cdutil,os,sys

f=cdms.open(os.path.join(sys.prefix,'sample_data','tas_mo.nc'))
s=f('tas')

print s.shape
tc=s.getTime().asComponentTime()

print tc[0],tc[-1]

cdutil.setTimeBoundsMonthly(s)
ref=cdutil.ANNUALCYCLE.climatology(s(time=('1980','1985','co')))
print ref.shape
dep=cdutil.ANNUALCYCLE.departures(s)
print 'dep',dep.shape
dep=cdutil.ANNUALCYCLE.departures(s,ref=ref)
print 'dep',dep.shape
