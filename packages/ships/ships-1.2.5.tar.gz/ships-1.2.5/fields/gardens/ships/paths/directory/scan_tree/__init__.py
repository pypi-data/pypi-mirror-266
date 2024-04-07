

'''
	import ships.paths.directory.scan_tree as scan_tree
	import ships.paths.directory.scan_tree.DFS as DFS
	the_tree_scan = scan_tree.thoroughly (cryo)
	
	places = []
	def place_found (place):
		places.append (place)

	DFS.thoroughly (the_tree_scan, place_found)
'''

'''
{
    "name": "root",
    "variety": "directory",
    "children": [
        {
            "name": "dir1",
            "variety": "directory",
            "children": [
                {"name": "file1.txt", "variety": "file"},
                {"name": "file2.txt", "variety": "file"}
            ]
        },
        {
            "name": "dir2",
            "variety": "directory",
            "children": [
                {"name": "file3.txt", "variety": "file"}
            ]
        },
        {"name": "file4.txt", "variety": "file"}
    ]
}
'''

import os
import json
from pathlib import Path

from ships.paths.variety import path_variety

def thoroughly (
	original_path,
	include_full_path = False
):
	the_variety = path_variety (original_path)
	if (the_variety != "directory"):
		return {
			'name': os.path.basename (original_path), 
			
			** ({ "path": original_path } if include_full_path else {}),
			
			#'path': directory,
			'rel_path': "",
			'variety': the_variety, 
			'children': []
		}
	
	original_scan_directory = str (original_path)

	def scan (directory):
		tree = {
			'name': os.path.basename (directory), 
			** ({ "path": directory } if include_full_path else {}),
			
			'rel_path': str (Path (directory).relative_to (
				Path (original_scan_directory)
			)),
			'variety': 'directory', 
			'children': []
		}

		# Iterate over the contents of the directory
		for item in os.listdir (directory):
			item_path = os.path.join (directory, item)

			variety = path_variety (item_path)			
			if (variety == "directory"):
				tree ['children'].append (scan (item_path))

			else:
				tree ['children'].append({
					'name': item, 
					
					** ({ "path": item_path } if include_full_path else {}),
					
					'rel_path': str (Path (item_path).relative_to (
						Path (original_scan_directory)
					)),
					'variety': variety
				})

		return tree
	
	return scan (original_scan_directory)
	
	





