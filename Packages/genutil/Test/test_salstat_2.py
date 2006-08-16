import genutil,cdms,cdutil

f=cdms.open('/pcmdi/obs/mo/tas/rnl_ncep/tas.rnl_ncep.ctl')
s1=f('tas',slice(0,120))
s2=f('tas',slice(-120,None))
print s1.shape,s2.shape

cstat=genutil.statistics.correlation(s1,s2,biased=0,centered=0)
csal1=genutil.salstat.PearsonsCorrelation(s1,s2)[0]
print csal1
csal2=genutil.salstat.SpearmansCorrelation(s1,s2)[0]
print csal2

d1=cstat-csal1
d2=cstat-csal2

print genutil.minmax(d1),cdutil.averager(d1,axis='xy')
print genutil.minmax(d2),cdutil.averager(d2,axis='xy')
