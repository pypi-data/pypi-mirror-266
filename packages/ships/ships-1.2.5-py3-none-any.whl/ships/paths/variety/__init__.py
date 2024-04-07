

'''
	from ships.paths.variety import path_variety
	path_variety ("")
'''

import os

def path_variety (venue_path):
	if os.path.islink (venue_path):
		return "symlink"
		
	if os.path.isfile (venue_path):
		return "file"
	
	#
	#	symlinks that point to directories
	#	return isdir, so this needs to be
	#	after islink
	#
	if os.path.isdir (venue_path): 	
		return "directory"
		
	return "unknown"