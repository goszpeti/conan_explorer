import sys
from pathlib import Path

import xunitparser

for result_file in Path(".").glob("result*.xml"):
    ts, tr = xunitparser.parse(open(str(result_file)))
    if tr.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
