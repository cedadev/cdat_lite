"""
Simple attribute test for working with gdb.

"""

import cdms
f = cdms.open('foo.nc')
print type(f.bar[0])
