import cdms,cdutil,MA, MV, os, sys
cdms.setAutoBounds('on')

# centroid test

a=MV.masked_array(MV.array([0,0,0,0,0,0,0,0,0,0,0,0]),[0,1,1,1,1,1,1,1,1,1,1,0])
bounds=MA.array(
    [[0,31],
     [31,59],
     [59,90],
     [90,120],
     [120,151],
     [151,181],
     [181,212],
     [212,243],
     [243,273],
     [273,304],
     [304,334],
     [334,365]]
    )
ax=a.getAxis(0)
ax.setBounds(bounds)
#print cdutil.times.centroid(a,[-10,30]) 
print 'Centroid Normal:',cdutil.times.centroid(a,[0,365]) 
print 'Centroid Cyclic:',cdutil.times.cyclicalcentroid(a,[0,365]) 

f=cdms.open(os.path.join(sys.prefix,'sample_data','tas_mo.nc'))
s=f('tas')

cdutil.setTimeBoundsMonthly(s)
djf=cdutil.DJF(s)
djf=cdutil.DJF(s,criteriaarg=[.8,0.0001])
djf=cdutil.ANNUALCYCLE.climatology(s)
djf=cdutil.YEAR.departures(s)
