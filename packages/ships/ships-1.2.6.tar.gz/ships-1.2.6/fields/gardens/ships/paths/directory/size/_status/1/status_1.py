
'''
	python3 status.py 'paths/directory/size/_status/1/status_1.py'
'''

import ships.paths.directory.size as directory_size

def rel_path (directory):
	import pathlib
	this_directory = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	return normpath (join (this_directory, directory))

def check_1 ():
	dir_size = directory_size.find (
		directory_path = rel_path ("cryo")
	)
	
	dir_size_DU = directory_size.DU (
		directory_path = rel_path ("cryo")
	)
	
	print ("dir_size:", dir_size)
	print ("dir_size_DU:", dir_size_DU)

	return;
	
	
checks = {
	"check 1": check_1
}