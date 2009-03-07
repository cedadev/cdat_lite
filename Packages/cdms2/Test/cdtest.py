#!/usr/bin/env python

import os, sys
pyexe = sys.executable
try:
    import cu
    mlist = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17']
except ImportError:
    mlist = ['01','02','03','04','05','06','07','08','10','11','12','13','14','15','16','17']

os.system(pyexe + ' genTestDataset.py')
for n in mlist:
    os.system(pyexe + ' cdtest'+n+'.py')
