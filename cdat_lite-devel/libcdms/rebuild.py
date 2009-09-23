
import os
j = os.system('./install_script /usr/local/cdat-trunk /usr/local/cdat-trunk ;  1>LOG.rebuild')
if j:
    print 'Compilation failed'
    raise SystemExit, 1

