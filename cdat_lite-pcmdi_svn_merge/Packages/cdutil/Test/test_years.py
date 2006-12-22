#!/usr/bin/env python

import cdms,cdutil,sys,os
cdms.setAutoBounds('on')

f=cdms.open('/pcmdi/bsanter0/Model/PCM/VSGSuO/Xy/th_PCM_VSGSuO_am_xy_wf_r0000_0000.dic')
f = cdms.open(os.path.join(sys.prefix,'sample_data','th_yr.nc'))

th=f('th',time=slice(-3,None,1))
t=th.getTime()
cdutil.setTimeBoundsYearly(t)

print 'Shape of th:',th.shape,th.getTime().getBounds()[0]
dep=cdutil.YEAR.departures(th,statusbar=None)

print 'Shape of dep:',dep.shape
