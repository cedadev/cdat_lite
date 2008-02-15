#!/usr/bin/env python
# Adapted for numpy/ma/cdms2 by convertcdms.py

import xmgrace,gc,sys

print 'Test disabled'
sys.exit()

#x=xmgrace.xmgrace.init()
#x=xmgrace.xmgrace.init(pipe_file='tmp.txt',new_pipe=True,clean_on_exit=False)
#y=xmgrace.xmgrace.init(pipe_file='tmp.txt',new_pipe=False,clean_on_exit=False)
x=xmgrace.xmgrace.init(pipe_file='tmp.txt',new_pipe=True)
print 'ok'
y=xmgrace.xmgrace.init(pipe_file='tmp.txt',new_pipe=False)

import numpy.oldnumeric.ma as MA

a=MA.arange(0,1,.01)
x.plot(a)
b=MA.sin(a)

y.plot(b)
