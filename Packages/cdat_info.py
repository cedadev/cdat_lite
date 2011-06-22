"""
Keep the minimum configuration to get cdat_lite working here.
"""

CDMS_INCLUDE_DAP = 'no'
def version():
    from cdat_lite import __version__
    return __version__.split('.')
