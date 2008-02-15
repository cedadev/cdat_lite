#!/usr/bin/env python
# Adapted for numpy/ma/cdms2 by convertcdms.py

import numpy.oldnumeric as Numeric,genutil

a=Numeric.ones((15,25),'d')
print a.shape
print genutil.statistics.rank(a,axis=1)
print genutil.statistics.variance(a,axis=0)
