import cdms,genutil,cdutil,os,sys

#fnm='/pcmdi/obs/mo/tas/rnl_ncep/tas.rnl_ncep.ctl'
#f=cdms.open(fnm)
f=cdms.open(os.path.join(sys.prefix,'sample_data','tas_cru_1979.nc'))
s=f('tas',time=slice(0,2))

# last test should fail !
print "####################### Test 1 ################################"
axistest=[0,[1,2],'xy','12','(longitude)(latitude)','(dsffd)(latitude)']
for ax in axistest:
    print 'testing:',ax
    ierr=0
    try:
        v=genutil.statistics.variance(s,axis=ax)
    except:
        ierr=1
        pass
    if ax in [axistest[-1]] and ierr==0:
        raise 'Error it should have failed !!!!'

print "####################### Test 2 ################################"
v=genutil.statistics.variance(s,axis='012',weights=['unweighted','weighted','unweighted'])
print v.shape
v=genutil.statistics.variance(s,axis='12',weights='weighted')
print v.shape

print "####################### Test 3 ################################"
#fnm='/pcmdi/amip/mo/clt/bmrc-01a/clt_bmrc-01a.cdms'
#clt=cdms.open(fnm)('clt')
f=cdms.open(os.path.join(sys.prefix,'sample_data','clt.nc'))
clt=f('clt')
v=genutil.statistics.covariance(clt,clt,axis='(latitude)(longitude)',weights=['generate','generate'])
print v.shape

print "####################### Test 4 ################################"
a=genutil.statistics.variance(clt, axis='tyx',weights=['equal', 'generate', 'equal'])
print a.shape
a=genutil.statistics.variance(clt, axis='yx',weights=['generate', 'equal'])
print a.shape
a=genutil.statistics.variance(clt, axis='tx',weights=['equal', 'equal'])
print a.shape
a=genutil.statistics.variance(clt, axis='t',weights=['equal'])
print a.shape


print "####################### Test 5 ################################"
a=genutil.statistics.laggedcovariance(clt,clt,lag=4,axis='(time)(longitude)')
print a.shape




