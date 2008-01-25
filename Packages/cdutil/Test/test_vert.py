#!/usr/bin/env python


import cdutil

import cdms,vcs,sys,os
import vcs.test.support
bg = vcs.test.support.bg

f = cdms.open(os.path.join(sys.prefix,'sample_data','vertical.nc'))
Ps=f('PS')
U=f('U')
B=f('hybm')
A=f('hyam')
Po=f('variable_2')
P=cdutil.reconstructPressureFromHybrid(Ps,A,B,Po)

U2=cdutil.logLinearInterpolation(U,P)

x=vcs.init()
x.plot(U2,bg=bg)
vcs.test.support.check_plot(x)
