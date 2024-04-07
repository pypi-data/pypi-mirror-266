

'''

'''
def thoroughly (
	json_tree, 
	callback,
	include_full_path = False
):
	# Recursive case: If the node is a directory, recursively traverse its children
	if json_tree ['variety'] == 'directory':
		processed_children = []
		
		assert ("children" in json_tree), json_tree
		
		for child in json_tree ['children']:
			DFS_proceeds = thoroughly (child, callback, include_full_path = include_full_path)
			processed_children.extend (DFS_proceeds)
			
		callback ({
			** ({ "path": json_tree ["path"] } if include_full_path else {}),
			"rel_path": json_tree ["rel_path"],
			"variety": json_tree ["variety"],
			"name": json_tree ["name"]
		})
		
		# Include current directory in processed nodes
		return processed_children + [ json_tree ['name'] ] 
	
	else:
		callback ({
			** ({ "path": json_tree ["path"] } if include_full_path else {}),
			"rel_path": json_tree ["rel_path"],
			"variety": json_tree ["variety"],
			"name": json_tree ["name"]
		})
		
		return []
