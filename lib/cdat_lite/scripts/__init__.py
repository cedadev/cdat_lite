"""
A wrapper package to embed CDAT scripts in the cdat_lite egg.

@author: Stephen pascoe
"""

import sys


def cdscan_main():
    """Setuptools compatable entry point to cdscan.
    """
    import cdscan
    cdscan.main(sys.argv)
    
def cddump_main():
    """Setuptools compatible entry point to cddump.

    cddump doesn't have a main function.  Just import-and-go.
    """
    import cddump

def convertcdms_main():
    """Setuptools compatable entry point for convertcdms.
    """
    import convertcdms
    convertcdms.main(sys.argv[1:])


def cfchecks_main():
    """cfchecks_main is based on the main program block in cfchecks.py
    """
    from cdat_lite.scripts.cfchecks import getargs, CFChecker
    from sys import argv,exit

    (badc,coards,uploader,useFileName,standardName,areaTypes,udunitsDat,version,files)=getargs(argv)
    
    inst = CFChecker(uploader=uploader, useFileName=useFileName, badc=badc, coards=coards, cfStandardNamesXML=standardName, cfAreaTypesXML=areaTypes, udunitsDat=udunitsDat, version=version)
    for file in files:
        rc = inst.checker(file)
        exit (rc)


