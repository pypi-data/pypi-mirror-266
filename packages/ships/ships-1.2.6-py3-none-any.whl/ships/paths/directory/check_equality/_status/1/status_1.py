

'''
	python3 status.proc.py "paths/directory/check_equality/_status/1/status_1.py"
'''

import ships.paths.directory.check_equality as check_equality

def rel_path (this_trail):
	import pathlib
	this_directory = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	return normpath (join (this_directory, this_trail))

def check_1 ():
	report = check_equality.start (
		rel_path ("directories/EQ_1"),
		rel_path ("directories/EQ_2")
	)	
	assert (
		{'1': {}, '2': {}} ==
		report
	)
	
checks = {
	"EQ check without differences": check_1
}