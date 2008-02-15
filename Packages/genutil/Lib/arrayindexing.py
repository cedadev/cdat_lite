# Adapted for numpy/ma/cdms2 by convertcdms.py
import numpy.oldnumeric as Numeric
#from statistics import __checker
import statistics
import numpy.oldnumeric.ma as MA,cdms2 as cdms,genutil
def get(Array,Indices,axis=0):
    """
    Arrayrrayindexing returns Array[Indices], indices are taken along dimension given with axis
    
    Usage:
    C=get(Array,Indices,axis=0) # i.e. C=Array[Indices]
    Indices accepts negative value ,e.g: -1 is last element
    """
    ## First some checks
    isma=MA.isMA(Array)
    if isinstance(Indices,int):
        return Array[Indices]
    if Indices.dtype.char not in [Numeric.Int,Numeric.Int32,Numeric.Int16]:
        raise "Error indices array must be made of integers (try: Indices=Indices.astype('l') first)"
    
    if cdms.isVariable(Array) :
        xatt=Array.attributes
        id=Array.id
        
    if len(Array.shape)!=len(Indices.shape):
        Array,Indices,weights,axis,ax=statistics.__checker(Array,Indices,None,axis,smally=1)
        if isinstance(Indices,int):
            return Array[Indices]
        if Indices.shape!=Array.shape[1:]:
            raise "Error uncompatible shapes: "+str(Array.shape)+" and "+str(Indices.shape)
    else:
        Array,Indices,weights,axis,ax=statistics.__checker(Array,Indices,None,axis)
        if Indices.shape!=Array.shape:
            raise "Error uncompatible shapes: "+str(Array.shape)+" and "+str(Indices.shape)

    m=Array.mask
    if not isinstance(Indices,int): Indices=Indices.raw_data() # Sometihng happened with masking of y by x mask
    C=genutil.array_indexing_emulate.extract(Array.raw_data(),Indices)
    if m is not MA.nomask:
        M=genutil.array_indexing_emulate.extract(m,Indices)
        C=MA.masked_where(M,C,copy=0)
    elif isma:
        C=MA.array(C,copy=0,mask=None)
    if not ax is None:
        C=cdms.createVariable(C,axes=ax,id=id,copy=0)
        for at in xatt.keys():
            setattr(C,at,xatt[at])
    return C

def set(Array,Indices,Values,axis=0):
    """
    Arrayrrayindexing set Array[Indices] with Values, indices are taken along dimension given with axis
    
    Usage:
    Array=set(Array,Indices,Values,axis=0) # i.e. Array[Indices]=Values

    Indices accepts negative value ,e.g: -1 is last element
    """
    ## First some checks
    #isma=MA.isMA(Array)
    if Indices.dtype.char not in [Numeric.Int,Numeric.Int32,Numeric.Int16]:
        raise "Error indices array must be made of integers (try: Indices=Indices.astype('l') first)"
    
    if cdms.isVariable(Array) :
        xatt=Array.attributes
        id=Array.id
    if len(Array.shape)!=len(Indices.shape):
        crap,Indices,crap,axis,ax=statistics.__checker(Array,Indices,None,axis,smally=1)
        Array,Values,crap,axis,ax=statistics.__checker(Array,Values,None,axis,smally=1)
        if Indices.shape!=Array.shape[1:]:
            raise "Error uncompatible shapes: "+str(Array.shape)+" and "+str(Indices.shape)
    else:
        Array,Indices,Values,axis,ax=statistics.__checker(Array,Indices,Values,axis)
        if Indices.shape!=Array.shape:
            raise "Error uncompatible shapes: "+str(Array.shape)+" and "+str(Indices.shape)

    m=Array.mask
    mv=Values.mask
    Indices=Indices.raw_data() # Sometihng happened with masking of y by x mask
    genutil.array_indexing_emulate.set(Array.raw_data(),Indices,Values.raw_data())
    if m is not MA.nomask:
        if mv is not MA.nomask:
            genutil.array_indexing_emulate.set(m,Indices,mv)
    elif mv is not MA.nomask:
        m=Numeric.zeros(mv.shape,mv.typcode())
        genutil.array_indexing_emulate.set(m,Indices,mv)
        if not MA.allequal(m,0):
            Array=MA.masked_where(m,Array,copy=0)
    if not ax is None:
        Array=cdms.createVariable(C,axes=ax,id=id,copy=0)
        for at in xatt.keys():
            setattr(C,at,xatt[at])
    return Array

 
