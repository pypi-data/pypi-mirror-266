# This block adds the RegexRiot directory onto the path
import os, sys
root = os.path.join(__file__, '..')
root = os.path.realpath(root)
sys.path.append(root)
del os, sys, root
#######################################################

from _basic_expressions import *
from _riot import *
