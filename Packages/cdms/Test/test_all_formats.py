import cdms,os,sys

try:
    print 'Dap ?'
    f=cdms.open('http://ferret.wrc.noaa.gov/cgi-bin/nph-nc/data/COADS_climatology.nc')
    print f.listvariables()
except:
    print 'Not Ok'

try:
    print 'PP ?'
    f=cdms.open(os.path.join(sys.prefix,'sample_data','testpp.pp'))
    print f.listvariables()
except:
    print 'Not Ok'

try:
    print 'HDF ?'
    f=cdms.open(os.path.join(sys.prefix,'sample_data','tdata.hdf'))
    print f.listvariables()
except:
    print 'Not Ok'

try:
    print 'DAP and Scientific ?'
    import Scientific.IO.NetCDF
    f=Scientific.IO.NetCDF.NetCDFFile('http://ferret.wrc.noaa.gov/cgi-bin/nph-nc/data/COADS_climatology.nc')
    print f.variables
except:
    print 'Not Ok'

try:
    print 'DRS ?'
    f=cdms.open('/pcmdi/bsanter1/Model/PCM/O/Xy/ta_300_850_PCM_O_mm_xy_wa_r0000_0000.dic')
    print f.listvariables()
except:
    print 'Not Ok'
    
try:
    print 'cmds/ql ?'
    f=cdms.open(os.path.join(sys.prefix,'sample_data','test.cdms'))
    print f.listvariables()
except Exception,err:
    print 'Not Ok',err
