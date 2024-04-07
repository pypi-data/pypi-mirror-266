

from .is_dir import is_dir

from os.path import normpath, join

def get_directories (LIST, BASE_PATH):
	DIRS = []

	for _LOCATION in LIST:
		ABS_LOCATION = join (BASE_PATH, _LOCATION)
		REL_LOCATION = _LOCATION
			
		if (is_dir (ABS_LOCATION)):
			DIRS.append (ABS_LOCATION)

	return DIRS;