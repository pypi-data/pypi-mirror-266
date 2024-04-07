
'''
	Description:
		Maybe this finds and replaces strings in the contents
		of "files" in the glob...?
'''

'''
	import ships.paths.directory.find_and_replace_string_v2 as find_and_replace_string_v2

	import pathlib
	from os.path import dirname, join, normpath
	this_folder = pathlib.Path (__file__).parent.resolve ()
	find_and_replace_string_v2.start (
		the_path = str (this_folder) + "/DB",

		find = 'region 1',
		replace_with = 'region one',
		
		replace_contents = "yes",
		replace_paths = "yes"
	)
'''

'''
	import glob
	glob.glob ('./[0-9].*')
'''

import glob
import os.path
import os
import shutil

import rich

import ships.paths.directory.scan_tree as scan_tree
import ships.paths.directory.scan_tree.DFS as DFS
	
from ships.paths.variety import path_variety

def retrieve_paths (the_path):
	paths_found = []
	if (path_variety (the_path) != "directory"):
		pass;

	the_tree_scan = scan_tree.thoroughly (the_path, include_full_path = True)
	#rich.print_json (data = the_tree_scan)
	
	
	def place_found (place):
		paths_found.append (place)

	DFS.thoroughly (the_tree_scan, place_found, include_full_path = True)	

	return paths_found

def start (
	the_path = "",
	
	find = "",
	replace_with = "",
	
	replace_contents = "yes",
	replace_paths = "yes",
	
	records = 0
):
	paths_found = retrieve_paths (the_path)	

	exceptions = []

	content_replacements = []
	if (replace_contents == "yes"):
		for path in paths_found:
			#print ("path:", path)
			
			variety = path ["variety"]
			prev_full_path = path ["path"]
			rel_path = path ["rel_path"]
		
			if (variety == "file"):		
				try:
					#
					#	open the original, and create a modified version
					#
					with open (prev_full_path) as FP_1:
						original = FP_1.read ()
						new_string = original.replace (find, replace_with)
				
					#
					#	if the modified version is different than the original
					#	then 
					#
					if (original != new_string):
						with open (prev_full_path, "w") as FP_2:
							FP_2.write (new_string)
				
						content_replacements.append (rel_path)
				except Exception:
					exceptions.append (path)

	
	path_replacements = []
	if (replace_paths == "yes"):
		for path in paths_found:
			variety = path ["variety"]
			
			
			#new_prev_full_path = prev_full_path.replace (find, replace_with)
			
			#os.path.basename (file_path)
			
			print ("path name:", path ["name"])
			prev_name = path ["name"]
			next_name = prev_name.replace (find, replace_with)
			
			
			if (prev_name == next_name):
				continue;
			
			prev_full_path = path ["path"]
			next_full_path = os.path.join (
				os.path.dirname (path ["path"]),
				next_name
			)
			
			prev_rel_path = path ["rel_path"]
			next_rel_path = os.path.join (
				os.path.dirname (path ["rel_path"]),
				next_name
			)
			
			if (variety == "directory"):
				print ('moving directory', prev_rel_path, next_full_path)
			
				shutil.move (prev_full_path, next_full_path)
				
				path_replacements.append ({
					"prev_rel_path": prev_rel_path,
					"next_rel_path": next_rel_path
				})
			
			elif (variety in [ "symlink", "file" ]):
				print ('moving other', prev_rel_path, next_full_path)
				
				os.rename (prev_full_path, next_full_path)
				
				path_replacements.append ({
					"prev_rel_path": prev_rel_path,
					"next_rel_path": next_rel_path
				})
			
			else:
				stringified = json.dumps (path, indent = 4)
			
				raise Exception (f"""
				
	The variety of this could not be found:
		
		{ stringified }
				
				""")
		


	return {
		"content_replacements": content_replacements,
		"path_replacements": path_replacements,
		"exceptions": exceptions
	}