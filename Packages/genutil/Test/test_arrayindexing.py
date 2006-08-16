import Numeric
import genutil
import cdms
import MA
import RandomArray
import os
import sys

### EXTRACT TESTS

### 1D

A=Numeric.array([6,7,8,9,2],'f')
B=Numeric.argsort(A)
print A
print B
C=genutil.arrayindexing.get(A,B)
print C
D=Numeric.array([6.5,7.5,8.5,9.5,2.5],'f')
print D
E=genutil.arrayindexing.set(A,B,D)
print E

## 2D
A=Numeric.array([[1,2],[3,4,],[5,6],[7,8]],Numeric.Float)

print A.shape,A.typecode()
print A[0]
print A[1]
print A[2]
print A[3]

B=Numeric.array([3,2],Numeric.Int)

C=genutil.array_indexing.extract(A,B)
print C,C.typecode()
C=genutil.arrayindexing.get(A,B)
print C,C.typecode()

f=cdms.open(os.path.join(sys.prefix,'sample_data','clt.nc'))
clt=f('clt')
## clt=cdms.MV.average(clt,2)
print clt.shape

M=MA.maximum.reduce(clt,axis=0)
marg=MA.argmax(clt,axis=0)
M2=genutil.arrayindexing.get(clt,marg)

print M2.shape,M2.mask(),genutil.minmax(M2-M)

M=MA.maximum.reduce(clt,axis=1)
marg=MA.argmax(clt,axis=1)
marg=cdms.MV.array(marg)
marg.setAxis(0,clt.getAxis(0))
marg.setAxis(1,clt.getAxis(2))
print clt.typecode(),M.shape
M2=genutil.arrayindexing.get(clt,marg,axis=1)

print M2.shape,M2.mask(),genutil.minmax(M2-M)

clt=cdms.MV.masked_greater(clt,80)
M=MA.maximum.reduce(clt,axis=1)
print M.mask(),'is the mask'
marg=MA.argmax(clt,axis=1)
marg=cdms.MV.array(marg)
marg.setAxis(0,clt.getAxis(0))
marg.setAxis(1,clt.getAxis(2))
print clt.typecode(),M.shape
M2=genutil.arrayindexing.get(clt,marg,axis=1)
print M2.shape,M2.mask(),genutil.minmax(M2-M)

## 3D
I=RandomArray.random(clt.shape)*clt.shape[0]
I=I.astype('i') # integers required
M2=genutil.arrayindexing.get(clt,I)

#### Set tests
V=Numeric.array([1345,34],A.typecode())
B=Numeric.array([-3,2],Numeric.Int)
A=genutil.arrayindexing.set(A,B,V)
print A

A=Numeric.array([[1,2],[3,4,],[5,6],[7,8]],Numeric.Float)
B=Numeric.array([[1,2],[3,0,],[1,2],[0,3]],Numeric.Int)
V=Numeric.array([[10.,21.],[13,.4,],[1.5,6.4],[77.7,9.8]],Numeric.Float)
C=genutil.arrayindexing.set(A,B,V)
print A
print C

## ## Test with mask
## I=RandomArray.random(clt.shape)*clt.shape[0]
## I=I.astype('i') # integers required
## clt2=genutil.arrayindexing.set(clt,I,clt)

## import vcs
## x=vcs.init()
## x.plot(clt2)
## raw_input("HJ")
