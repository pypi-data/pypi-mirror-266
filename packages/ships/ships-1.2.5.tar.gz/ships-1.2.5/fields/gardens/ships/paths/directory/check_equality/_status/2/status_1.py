



'''
	python3 status.py "paths/directory/check_equality/_status/2/status_1.py"
'''

import ships.paths.directory.check_equality as check_equality

def rel_path (DIRECTORY):
	import pathlib
	FIELD = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	return normpath (join (FIELD, DIRECTORY))

def check_1 ():
	revenue = check_equality.start (
		rel_path ("directories/EQ_1"),
		rel_path ("directories/EQ_2")
	)	
	
		
	assert (
		{
			'1': {
				'1.HTML': 'f', 
				'1/1.HTML': 'f'
			}, 
			'2': {
				'2': 'd', 
				'2.HTML': 'f', 
				'1/2.HTML': 'f'
			}
		} ==
		revenue
	)
	
checks = {
	"EQ check with differences": check_1
}