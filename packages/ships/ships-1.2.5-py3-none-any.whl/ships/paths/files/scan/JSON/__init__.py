
'''
field = pathlib.Path (__file__).parent.resolve ()
full_path = normpath (join (field, path))

import ships.paths.path.relative as relative_path
import ships.paths.files.scan.JSON as scan_JSON_path

scan_JSON_path.start (relative_path.pave ("proceeds.JSON"))
'''

from os.path import dirname, join, normpath
import sys
import json
import pathlib

def start (path):
	field = pathlib.Path (__file__).parent.resolve ()
	full_path = normpath (join (field, path))
	
	with open (full_path) as selector:
		note = json.load (selector)
	
	return note