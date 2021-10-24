import sys
from pathlib import Path

import xunitparser

""" Read all result*.xml files and throw an exit code 1, if there was a failure. """
for result_file in Path(".").glob("result*.xml"):
    ts, tr = xunitparser.parse(open(str(result_file)))
    if not tr.wasSuccessful():
        sys.exit(1)
sys.exit(0)
