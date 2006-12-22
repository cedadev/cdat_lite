#!/usr/bin/env python

var='tas'
amipmodel='dnm-98a'
import cdtime,cdms,os,sys
from cdutil import times
from cdms import MV

cdms.setAutoBounds('on')

f   = cdms.open(os.path.join(sys.prefix,'sample_data','tas_mo.nc'))
fsc = cdms.open(os.path.join(sys.prefix,'sample_data','tas_mo_clim.nc'))

print "0: reading data"
s=f(var,longitude=(0,360,'co'))

acok=fsc('climseas',longitude=(0,360,'co'))

print 'Test #1 : Test result'

ac=times.JAN.climatology(s)

if not(MV.allclose(ac[0],acok[0])) : raise 'Err answer seems to be wrong we Missing Value free dataset'

f.close()
fsc.close()

a=cdtime.comptime(1980)
b=cdtime.comptime(1980,5)

f = cdms.open(os.path.join(sys.prefix,'sample_data','tas_6h.nc'))
s=f(var,time=(a,b,'co'),squeeze=1)

print "Test #2: 6hourly AND get"
jans=times.JAN(s)
try:
    jans=times.JAN(s)
except:
     raise 'Error computing januarys from 6h'

print "Test #3: climatology 6h"
JFMA=times.Seasons('JFMA')
try:
    jfma=JFMA.climatology(s)
except:
    raise 'Error computing climatological JFMA from 6h'


#Test reorder
print "Test #4: time not first axis"
try:
    jfma=JFMA.climatology(s(order='x...'))
except:
    raise 'Error in (un)ordered slab, computing climatology'

print "Test 4b: Result ok ?"
if jfma.getOrder()[0]!='x' : raise "Error output order is  wrong"



