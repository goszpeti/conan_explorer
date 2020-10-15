import sys

import xunitparser

ts, tr = xunitparser.parse(open("result.xml"))
if tr.wasSuccessful():
    sys.exit(0)
else:
    sys.exit(1)
