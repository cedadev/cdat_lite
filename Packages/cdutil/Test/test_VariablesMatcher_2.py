#!/usr/bin/env python

"""In this example we now retrieve NCEP and ECMWF for the year 1981, mask the land on their grid and apply an external data mask (the JONES variable). Finally the variables are once again put on the 10x10 grid where we apply a mask. Try not apply the mask on the final grid and note the difference (tip: to do so, simply change the definition of FG to: FG=cdutil.MaskedGridMaker() )
"""

import cdutil, vcs
# First let's creates the mask (it is the same for NCEP and ECMWF since they are on the same grid).
refmsk='/pcmdi/obs/etc/sftl.25deg.ctl'
M=cdutil.WeightsMaker(refmsk, var='sftl', values=[1.])
# Reference
ref='/pcmdi/obs/mo/tas/rnl_ecm/tas.rnl_ecm.sfc.ctl'
Ref=cdutil.VariableConditioner(ref, weightsMaker=M)
Ref.var='tas'
Ref.id='ECMWF'
Ref.cdmsKeywords={'time':('1981','1982','co')}
# Test
tst='/pcmdi/obs/mo/tas/rnl_ncep/tas.rnl_ncep.ctl'
Tst=cdutil.VariableConditioner(tst, weightsMaker=M)
Tst.var='tas'
Tst.id='NCEP'
# External Variable (for the mask)
ext='/pcmdi/obs/mo/tas/jones_amip/tas.jones_amip.ctl'
EV=cdutil.VariableConditioner(ext)
EV.var='tas'
EV.id='JONES'
# Final Grid
# We need a mask for the final grid
fgmask='/pcmdi/staff/longterm/doutriau/ldseamsk/amipII/pcmdi_sftlf_10x10.nc'
M2=cdutil.WeightsMaker(source=fgmask, var='sftlf', values=[100.])
FG=cdutil.WeightedGridMaker(weightsMaker=M2)
FG.longitude.n=36
FG.longitude.first=0.
FG.longitude.delta=10.
FG.latitude.n=18
FG.latitude.first=-85.
FG.latitude.delta=10.
# Now creates the compare object
c=cdutil.VariablesMatcher(Ref, Tst, weightedGridMaker=FG, externalVariableConditioner=EV)
# And gets it
(ref, reffrc), (test, tfrc) = c()
print 'Shapes:', test.shape, ref.shape
# Plots the difference
x=vcs.init()
x.plot(test-ref)
# Wait for user to press return
raw_input("Press enter")
