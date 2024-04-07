


'''
CAUTION: HAS ACCESS TO SHELL
'''

'''
import ships.paths.directory.size as directory_size
directory_size.find (
	directory_path = ""
)
'''

'''
https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
'''

import subprocess
from os.path import dirname, join, normpath
from pathlib import Path

def find (
	directory_path = ""
):
	try:
		return sum (
			p.stat ().st_size for p in Path (directory_path).rglob ('*')
		)
	except Exception as E:
		print (E)
		
	return "?"


def DU (
	directory_path = ""
):
	size = subprocess.run (
		f"du -sh '{ directory_path }'",
		
		shell = True, 
		check = True,
		
		capture_output = True, 
		text = True,
		cwd = normpath (join (dirname (__file__)))
	).stdout.strip ("\n")
	
	return size
