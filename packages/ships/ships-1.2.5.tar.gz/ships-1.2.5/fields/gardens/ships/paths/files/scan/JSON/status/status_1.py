



'''
	python3 status.py 'paths/files/scan/**/status_*.py'
'''

import ships.cycle as cycle
import time
from fractions import Fraction
import shutil

import ships.paths.files.scan.JSON as scan_JSON_path

import pathlib
from os.path import dirname, join, normpath

def check_1 ():
	this_folder = pathlib.Path (__file__).parent.resolve ()

	note = scan_JSON_path.start (
		normpath (join (this_folder, "../cryo/example.JSON"))
	)
	
	assert (note ["field"] == 1)
	
	print (note)
	
checks = {
	"runs without exceptions": check_1
}




#