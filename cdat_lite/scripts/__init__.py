"""
A wrapper package to embed CDAT scripts in the cdat_lite egg.

@author: Stephen pascoe
"""

import sys

import cdscan

def cdscan_main():
    """Setuptools compatable entry point to cdscan.
    """
    cdscan.main(sys.argv)
    
