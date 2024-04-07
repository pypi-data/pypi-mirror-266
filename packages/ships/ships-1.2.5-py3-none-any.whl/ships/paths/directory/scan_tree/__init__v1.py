



'''
	
'''

'''
	itinerary:
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

def thoroughly (directory):
	the_base_directory = directory

	def scan (current_directory):
		relative_path = Path (current_directory).relative_to (
			Path (the_base_directory)
		)
	
		tree = {
			'name': os.path.basename (directory), 
			'rel path': str (relative_path),
			'path': directory,
			'variety': 'directory', 
			'children': []
		}

		# Iterate over the contents of the directory
		for item in os.listdir (directory):
			item_path = os.path.join (directory, item)

			# If the item is a subdirectory, recursively build its tree
			if os.path.isdir(item_path):
				tree ['children'].append (scan (item_path))
			else:
				tree ['children'].append({
					'name': item, 
					'path': item_path,
					'variety': 'file'
				})
				
		return tree;

	return scan (directory)
	
	
def DFS (json_tree, callback):
	if json_tree ['variety'] == 'file':
		callback ({
			"path": json_tree ["path"],
			"variety": json_tree ["variety"]
		})
		
		return []
		
	# Recursive case: If the node is a directory, recursively traverse its children
	else:
		processed_children = []
		for child in json_tree ['children']:
			DFS_proceeds = DFS (child, callback)
			processed_children.extend (DFS_proceeds)
			
		callback ({
			"path": json_tree ["path"],
			"variety": json_tree ["variety"]
		})
		
		return processed_children + [ json_tree ['name'] ]  # Include current directory in processed nodes





