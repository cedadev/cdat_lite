# From cdms/Test/makeError.py
# We don't use the error marking infrastructure but some of the test data
# is created here.

import MA

NTIME = 3
NLAT = 16
NLON = 32

x = MA.arange(float(2*NTIME*NLAT*NLON))
x.shape=(2,NTIME,NLAT,NLON)
