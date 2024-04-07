
'''
import ships.paths.path.relative as relative_path
relative_path.pave (path)
'''

'''
	
'''

import inspect
import os
from os.path import dirname, join, normpath

def pave (path):
	file_path_of_caller_function = os.path.abspath (
		(inspect.stack () [1]) [1]
	)

	return normpath (join (file_path_of_caller_function, path))