

'''
	python3 status.py "paths/directory/equalize/_status/2/status_1.py"
'''


import ships.paths.directory.deallocate as deallocate_dir
import ships.paths.directory.equalize as equalize

import json

def rel_path (directory):
	import pathlib
	this_directory = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	return normpath (join (this_directory, directory))

def check_1 ():
	start = rel_path ("start")
	end = rel_path ("end")

	print ("start:", start)
	print ("end:", end)

	try:
		deallocate_dir.beautifully (end)
	except Exception as E:
		print (E)

	revenue = equalize.multiple ({
		"directory 1": start,
		"directory 2": end,
		
		"directories": [
			"1",
			"2",
			"3"
		],
		
		"start": "yes"	
	})
	
	#
	#	The sizes might be different on another FS
	#
	assert (
		revenue ==
		[
			{
				"EQ check": {
					"1": {},
					"2": {}
				},
				"sizes": {
					"from": 10,
					"to": 10
				}
			},
			{
				"EQ check": {
					"1": {},
					"2": {}
				},
				"sizes": {
					"from": 4103,
					"to": 4103
				}
			},
			{
				"EQ check": {
					"1": {},
					"2": {}
				},
				"sizes": {
					"from": 4100,
					"to": 4100
				}
			}
		]
	)
	
	deallocate_dir.beautifully (end)

	return;
	
	
checks = {
	"check 1": check_1
}