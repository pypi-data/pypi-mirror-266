

'''
	python3 status.py 'paths/directory/sense/_status/1/status_1.py'
'''

import shutil

import ships.paths.directory.sense as sense

	

def check_1 ():
	import pathlib
	from os.path import dirname, join, normpath
	this_folder = pathlib.Path (__file__).parent.resolve ()

	temp = normpath (join (this_folder, "temp"))
	cryo = normpath (join (this_folder, "cryo"))

	try:
		shutil.rmtree (temp)
	except Exception as E:
		print ("temp wasn't removed", E)

	#path = pathlib.Path (temp)
	#path.mkdir (parents = True)

	#from distutils.dir_util import copy_tree
	shutil.copytree (
		cryo,
		temp
	)

	def action (* pos, ** keys):
		print ("action:", action)
	
		return;

	'''
	import ships.paths.directory.sense as sense
	sense.changes (
		action = action,
		directory = temp
	)
	'''
	
	return;
	
checks = {
	'check 1': check_1
}