





'''
	python3 status.py "paths/directory/scan_tree/_status/1/status_1.py"
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
	cryo = rel_path ("cryo")
	
	the_tree_scan = scan_tree.thoroughly (
		cryo
	)
	rich.print_json (data = the_tree_scan)
	
	assert (
		the_tree_scan == {
		  "name": "cryo",
		  "rel_path": ".",
		  "variety": "directory",
		  "children": [
			{
			  "name": "3",
			  "rel_path": "3",
			  "variety": "directory",
			  "children": [
				{
				  "name": "3.txt",
				  "rel_path": "3/3.txt",
				  "variety": "file"
				},
				{
				  "name": "9",
				  "rel_path": "3/9",
				  "variety": "directory",
				  "children": [
					{
					  "name": "9.txt",
					  "rel_path": "3/9/9.txt",
					  "variety": "file"
					}
				  ]
				}
			  ]
			},
			{
			  "name": "symlink_to_1",
			  "rel_path": "symlink_to_1",
			  "variety": "symlink"
			},
			{
			  "name": "symlink_to_1.txt",
			  "rel_path": "symlink_to_1.txt",
			  "variety": "symlink"
			},
			{
				"name": "symlink_to_symlink_to_1",
				"rel_path": "symlink_to_symlink_to_1",
				"variety": "symlink"
			},
			{
			  "name": "1.txt",
			  "rel_path": "1.txt",
			  "variety": "file"
			},
			{
			  "name": "2",
			  "rel_path": "2",
			  "variety": "directory",
			  "children": [
				{
				  "name": "2.txt",
				  "rel_path": "2/2.txt",
				  "variety": "file"
				},
				{
				  "name": "55",
				  "rel_path": "2/55",
				  "variety": "directory",
				  "children": [
					{
					  "name": "55.txt",
					  "rel_path": "2/55/55.txt",
					  "variety": "file"
					}
				  ]
				}
			  ]
			},
			{
			  "name": "1",
			  "rel_path": "1",
			  "variety": "directory",
			  "children": [
				{
				  "name": "1.py",
				  "rel_path": "1/1.py",
				  "variety": "file"
				}
			  ]
			}
		  ]
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
		[
		  {
			"rel_path": "3/3.txt",
			"variety": "file",
			"name": "3.txt"
		  },
		  {
			"rel_path": "3/9/9.txt",
			"variety": "file",
			"name": "9.txt"
		  },
		  {
			"rel_path": "3/9",
			"variety": "directory",
			"name": "9"
		  },
		  {
			"rel_path": "3",
			"variety": "directory",
			"name": "3"
		  },
		  {
			"rel_path": "symlink_to_1",
			"variety": "symlink",
			"name": "symlink_to_1"
		  },
		  {
			"rel_path": "symlink_to_1.txt",
			"variety": "symlink",
			"name": "symlink_to_1.txt"
		  },
		  {
			"rel_path": "symlink_to_symlink_to_1",
			"variety": "symlink",
			"name": "symlink_to_symlink_to_1"
		  },
		  {
			"rel_path": "1.txt",
			"variety": "file",
			"name": "1.txt"
		  },
		  {
			"rel_path": "2/2.txt",
			"variety": "file",
			"name": "2.txt"
		  },
		  {
			"rel_path": "2/55/55.txt",
			"variety": "file",
			"name": "55.txt"
		  },
		  {
			"rel_path": "2/55",
			"variety": "directory",
			"name": "55"
		  },
		  {
			"rel_path": "2",
			"variety": "directory",
			"name": "2"
		  },
		  {
			"rel_path": "1/1.py",
			"variety": "file",
			"name": "1.py"
		  },
		  {
			"rel_path": "1",
			"variety": "directory",
			"name": "1"
		  },
		  {
			"rel_path": ".",
			"variety": "directory",
			"name": "cryo"
		  }
		]
	), places
		
checks = {
	"check 1": check_1
}