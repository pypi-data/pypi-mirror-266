



def add_paths_to_system (paths):
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_folder = pathlib.Path (__file__).parent.resolve ()	
	for path in paths:
		sys.path.insert (0, normpath (join (this_folder, path)))

add_paths_to_system ([
	'../../../gardens_pip'
])



import pathlib
from os.path import dirname, join, normpath


this_directory = pathlib.Path (__file__).parent.resolve ()
fields = normpath (join (this_directory, "../../.."))
ships = normpath (join (fields, "gardens/ships"))

import sys
if (len (sys.argv) >= 2):
	glob_string = ships + '/' + sys.argv [1]
else:
	glob_string = ships + '/**/status_*.py'


print ("glob:", glob_string)

import bracelet
scan = bracelet.start (
	glob_string = glob_string,
	relative_path = ships,
	
	module_paths = [	
		normpath (join (fields, "gardens")),
		normpath (join (fields, "gardens_pip"))
	],
	
	simultaneous = True,
	
	db_directory = normpath (join (this_directory, "DB"))
)


#
#
#
