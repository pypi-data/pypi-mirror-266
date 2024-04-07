'''
import BOTANY.FS.DIRECTORY.for_each_path as for_each_path

import pathlib
from os.path import dirname, join, normpath
THIS_FOLDER = pathlib.Path (__file__).parent.resolve ()

#
#	git mv {path} {new path}
#
def fn (params):
	current_path_name = params ["current path name"]
	change_path = params ["change path"]
	change_path = params ["change path"]

	change_name (current_path_name.lower ())

for_each_path.start (
	glob_string = str (THIS_FOLDER) + "/DB/**/*",
	fn = fn
)
'''

'''
import glob

def start (
	glob_string = "",
	fn = lambda : ()
):
	paths = glob.glob (glob_string, recursive = True)

	def change_path (new_path):
		shutil.move ()

	def change_name (new_name):
		shutil.move ()

	for path in paths:
		fn ({
			"path": path,
			"change path": change_path
		})

'''