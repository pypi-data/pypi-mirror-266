

'''
import ships.paths.directory.equalize as equalize_dir
equalize_dir.multiple ({
	"directory 1": "",
	"directory 2": "",
	
	"directories": [
			
	],
	
	"size check": "du",
	
	"start": "no"	
})
'''

import ships.paths.directory.check_equality as check_equality
import ships.paths.directory.size as dir_size
import ships.paths.directory.rsync as rsync

from os.path import dirname, join, normpath
import os

import rich

import subprocess
def check_procedure_exists (procedure):
	try:
		subprocess.run(["which", procedure], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return True
	except subprocess.CalledProcessError:
		pass;
	
	print(f"The procedure '{procedure}' was not found.")

	return False

def multiple (shares):
	
	assert (check_procedure_exists ("rsync") == True), "The procedure 'rsync' was not found."

	directory_1 = shares ["directory 1"]
	directory_2 = shares ["directory 2"]
	directories = shares ["directories"]
	
	os.makedirs (directory_2, exist_ok = True)
	
	if ("start" in shares and shares ["start"] == "yes"):
		start = "yes"
	else:
		start = "no"
		
	if ("size check" in shares and shares ["size check"] == "du"):
		size_check = "du"
	else:
		size_check = "py"
	
	output = []
	
	for directory in directories:	
		from_dir = normpath (join (directory_1, directory))
		to_dir = normpath (join (directory_2, directory))
	
		rsync_script_string = rsync.process ({
			"from": from_dir,
			"to": to_dir,
			
			"start": start
		})
		
		if (start == "no"):
			print ("rsync_script_string:", rsync_script_string)
			
		EQ_report = check_equality.start (
			from_dir,
			to_dir
		)	
		
		
		assert (
			EQ_report ==
			{'1': {}, '2': {}}
		), rich.print_json (data = EQ_report)

		
		if (size_check == "du"):
			size_from_dir = dir_size.DU (
				directory_path = from_dir
			)
			size_to_dir = dir_size.DU (
				directory_path = to_dir
			)
			
		else: 
			size_from_dir = dir_size.find (
				directory_path = from_dir
			)
			size_to_dir = dir_size.find (
				directory_path = to_dir
			)
		
		output.append ({
			"EQ check": EQ_report,
			"sizes": {
				"from": size_from_dir,
				"to": size_to_dir
			}
		})
		
	return output