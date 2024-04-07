





'''
	python3 status.py "paths/directory/scan_tree/_status/2/status_1.py"
'''

import ships.paths.directory.scan_tree as scan_tree
import ships.paths.directory.scan_tree.DFS as DFS

import json
import rich

def rel_path (directory):
	import pathlib
	this_directory = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	return normpath (join (this_directory, directory))

def check_1 ():
	cryo = rel_path ("cryo.txt")
	
	the_tree_scan = scan_tree.thoroughly (cryo)
	rich.print_json (data = the_tree_scan)
	
	assert (
		the_tree_scan ==
		{
			"name": "cryo.txt",
			"rel_path": "",
			"variety": "file",
			"children": []
		}
	), the_tree_scan
	
	places = []
	def place_found (place):
		#rich.print_json (data = place)
		places.append (place)

	DFS.thoroughly (the_tree_scan, place_found)

	rich.print_json (data = places)
		
	assert (
		places ==
		[{
			"rel_path": "",
			"name": "cryo.txt",
			"variety": "file"
		}]
	), places
		
checks = {
	"check 1": check_1
}