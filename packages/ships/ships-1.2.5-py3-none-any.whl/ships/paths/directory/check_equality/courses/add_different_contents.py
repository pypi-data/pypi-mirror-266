

'''

'''

from .is_dir import is_dir

from os.path import isfile, islink
from os.path import join

def add_different_contents (RESULTS, BASE_PATH, LIST, REL_PREPEND = ""):
	for _LOCATION in LIST:
		ABS_LOCATION = join (BASE_PATH, _LOCATION)
		REL_LOCATION = REL_PREPEND + _LOCATION
	
		if (islink (ABS_LOCATION)):
			RESULTS ['1'] [REL_LOCATION] = "sc"
			RESULTS ['2'] [REL_LOCATION] = "sc"

		elif (isfile (ABS_LOCATION)):
			RESULTS ['1'] [REL_LOCATION] = "fc"
			RESULTS ['2'] [REL_LOCATION] = "fc"

		elif (is_dir (ABS_LOCATION)):
			RESULTS ['1'] [REL_LOCATION] = "dc"
			RESULTS ['2'] [REL_LOCATION] = "dc"

		else:
			RESULTS ['1'] [REL_LOCATION] = "?c"
			RESULTS ['2'] [REL_LOCATION] = "?c"