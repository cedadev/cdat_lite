"""
A reduced version of Ros' test suite to keep the size of the tarball
down.  These tests should be considered just a sanity check.

This module also tests the existence of the environment variable
UDUNITS2_HOME and only runs the tests if it is present.

"""

import sys, os, logging
log = logging.getLogger(__name__)

import tempfile, glob
import difflib
from subprocess import Popen, PIPE

# Ignore all except v1.0 tests
ignore = ['badc_units.nc', 'stdName_test.nc']
version_map = {
    'CF_1_2.nc': '1.2',
    'flag_tests.nc': '1.3',
    'Trac049_test1.nc': '1.4',
    'Trac049_test2.nc': '1.4',
    }


def _do_test(filename, checkfilename, version='1.0'):
    exe = sys.executable
    temp = tempfile.TemporaryFile()

    p1 = Popen([exe, '-c', 'import cdat_lite.scripts as s; s.cfchecks_main()'] + checker_args + ['-v', version] + [filename],
               stdout=temp,
               )
    p1.communicate()
    temp.seek(0)

    check_lines = open(checkfilename).readlines()
    test_lines = temp.readlines()

    diff = list(difflib.unified_diff(test_lines, check_lines))
    
    if len(diff) > 0:
        for line in diff:
            print line,
        assert False


def test():
    # We must be in the test directory for these to work.  However nose
    # does wierd things with current directories so be smart.
    try:
        here = os.getcwd()
    except OSError:
        here = '.'
    try:
        os.chdir(os.path.dirname(__file__))
        for file in glob.glob('*.nc'):
            if file in ignore:
                continue
            version = version_map.get(file, '1.0')
            checkfile = os.path.splitext(file)[0]+'.check'
            yield _do_test, file, checkfile, version
    finally:
        os.chdir(here)

try:
    udunits2_home = os.environ['UDUNITS2_HOME']
except KeyError:
    log.warning('Not running cfchecks tests.  Set UDUNITS2_HOME to run these tests')
    test.__test__ = False
else:
    udunits2_xml = os.path.join(udunits2_home, 'share', 'udunits', 'udunits2.xml')
    cf_table = os.path.join(os.path.dirname(__file__), 'cf-standard-name-table.xml')
    checker_args = ['-u', udunits2_xml, '-s', cf_table]

    if not os.path.exists(udunits2_xml):
        log.warning('Not running cfchecks tests.  Cannot find udunits2.xml')
        test.__test__ = False




