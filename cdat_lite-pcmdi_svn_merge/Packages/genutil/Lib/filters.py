import MA,cdms,MV,genutil

def custom1D(x,filter,axis=0):
    """
    Function: custom(x,filter,axis=0)
     
    Description of function:
        Apply a custom 1 dimensional filter to an array over a specified axis 
    Usage:
        filtered = covariance(unfiltered,filter)
    Options:
        axisoptions: 'x' | 'y' | 'z' | 't' | '(dimension_name)' | 0 | 1 ... | n 
            default value = 0. You can pass the name of the dimension or index
            (integer value 0...n) over which you want to compute the statistic.
    """
    isMV=cdms.isVariable(x)
    if isMV: xatt=x.attributes
    filter=MV.array(filter)
    newx=MV.array(x)
    initialorder=newx.getOrder(ids=1)
    n=len(filter)
    newx=newx(order=str(axis)+'...')
    sh=list(newx.shape)
    sh[0]=sh[0]-n+1
    out=MA.zeros(sh,typecode=newx.typecode())
    ax=[]
    bnds=[]
    nax=newx.getAxis(0)
    for i in range(sh[0]):
        sub=newx[i:i+n]
        if i==0:
            filter.setAxis(0,sub.getAxis(0))
            filter,sub=genutil.grower(filter,sub)
        out[i]=MA.average(sub,0,weights=filter)
        if isMV:
            a=nax.subAxis(i,i+n)
            try:
                b=a.getBounds()
                b1=b[0][0]
                b2=b[-1][1]
                ax.append((b1+b2)/2.)
                bnds.append([b1,b2])
            except: # No bounds on this axis
                bnds=None
                ax.append(float(MA.average(a[:])))
    out=MV.array(out,id=newx.id)
    if isMV:
        for k in xatt.keys():
            setattr(out,k,xatt[k])
        for i in range(1,len(sh)):
            out.setAxis(i,newx.getAxis(i))
        if not bnds is None: bnds=MA.array(bnds)
        ax=cdms.createAxis(ax,bounds=bnds)
        a=newx.getAxis(0)
        attr=a.attributes
        ax.id=a.id
        for k in attr.keys():
            setattr(ax,k,attr[k])
        out.setAxis(0,ax)
        
    out=out(order=initialorder)
    if not isMV:
        out=MA.array(out)
    return out


def smooth121(x,axis=0):
    """
    Function smooth121(x,axis=0)
     
    Description of function:
        Apply a 121 filter to an array over a specified axis 
    Usage:
        filtered = smooth121(unfiltered)
    Options:
        axisoptions: 'x' | 'y' | 'z' | 't' | '(dimension_name)' | 0 | 1 ... | n 
            default value = 0. You can pass the name of the dimension or index
            (integer value 0...n) over which you want to compute the statistic.
    """
    return custom1D(x,[1.,2.,1.],axis=axis)
    
def runningaverage(x,N,axis=0):
    """
    Function runningaverage(x,N,axis=0)
     
    Description of function:
        Apply a running average of length N to an array over a specified axis 
    Usage:
        smooth = runningaverage(x,12)
    Options:
        N: length of the running average
        axisoptions: 'x' | 'y' | 'z' | 't' | '(dimension_name)' | 0 | 1 ... | n 
            default value = 0. You can pass the name of the dimension or index
            (integer value 0...n) over which you want to compute the statistic.
    """
    filter=MA.ones((N,),typecode='f')
    return custom1D(x,filter,axis=axis)
