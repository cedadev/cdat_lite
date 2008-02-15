# Adapted for numpy/ma/cdms2 by convertcdms.py
"""writenetcdf
   see also dataset write method
"""
import cdms2 as cdms

def writenetcdf (slab, filename, mode="a"):
    """writenetcdf(slab, filename, mode="a") writes slab to the file.
       modes: 'a'  append
              'w'  replace
              'r'  replace (for legacy code only, deprecated)
       s can be anything asVariable will accept
    """
    if mode == 'r': mode = 'w'
    slab = cdms.asVariable(slab, 0)
    f = cdms.openDataset(filename, mode)
    f.write(slab)
    f.close()

if __name__ == '__main__':
    from numpy.oldnumeric.ma import allclose
    import pcmdi
    g = cdms.openDataset('clt.nc','r')
    c = g.variables['clt']
    t = cdms.asVariable([1.,2.,3.])
    t.id = 't'
    writenetcdf(c, 'test.nc', 'w')
    writenetcdf(t, 'test.nc', 'a')
    f = cdms.open('test.nc')
    d = f.variables['clt']
    assert allclose(c,d)
    for name in ['clt', 't']:
        pcmdi.slabinfo(f.variables[name])


