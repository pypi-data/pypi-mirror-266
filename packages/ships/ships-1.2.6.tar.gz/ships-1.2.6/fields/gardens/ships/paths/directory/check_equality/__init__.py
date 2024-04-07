
'''
	import ships.paths.directory.check_equality as check_equality
	report = check_equality.start (
		directory_1,
		directory_2
	)	
	assert (
		report ==
		{'1': {}, '2': {}}
	)
'''

from filecmp import dircmp
from filecmp import cmp

from os.path import isfile, islink, isdir
from os.path import relpath
from os.path import normpath, join

import json

from .courses.is_dir import is_dir
from .courses.get_directories import get_directories
from .courses.get_same_directories import get_same_directories
from .courses.add_different_paths import add_different_paths
from .courses.add_different_contents import add_different_contents

def start (
	D1, 
	D2, 


	#
	#	"yes" -> this returns the relative path to D1 & D2
	#		
	#	[not implemented] "no" -> RETURNS ABSOLUTE PATHS
	#
	relative_paths = "yes",
	
	#
	#	[not implemented]
	#
	#	IF DIRECTORIES ARE DIFFERENT,
	#	GO THROUGH AND LIST THE CONTENTS THAT DIFFER
	#	IN EACH DIRECTORY
	#
	ENUMERATE_UNIQUE_DIRECTORIES = "no"
):
	proceeds = {
		"1": {},
		"2": {}
	};
	
	#
	#	https://docs.python.org/3/library/filecmp.html#the-dircmp-class
	#
	DCMP = dircmp (
		D1, 
		D2, 
		
		#
		ignore = None, 
		hide = None
	);

	#print (DCMP.subdirs.values ());
	
	D1_LIST = DCMP.left_list
	D2_LIST = DCMP.right_list
	SAME_LIST = DCMP.common
	
	D1_FOLDERS = get_directories (D1_LIST, D1);
	D2_FOLDERS = get_directories (D2_LIST, D2);

	SAME_FOLDERS = get_same_directories (SAME_LIST, D1, D2);

	D1_ONLY = DCMP.left_only
	D2_ONLY = DCMP.right_only
	
	DIFFERENT_CONTENTS = DCMP.diff_files
	
	
	#
	#	FILES THAT ARE IN BOTH,
	#	BUT ARE NOT COMPARABLE (NO PERMISSIONS?)
	#
	INCOMPARABLE_FILES = DCMP.funny_files


	def COMPARE_LEVEL (REL_PATH, FOLDER_1, FOLDER_2):
		print ("COMPARE LEVEL", REL_PATH, json.dumps ({
			"1": FOLDER_1,
			"2": FOLDER_2
		}, indent = 2 ))
	
	
		COMPARISON = dircmp (
			FOLDER_1, 
			FOLDER_2, 
			
			#
			ignore = None, 
			hide = None
		);
	
		FOLDER_1_LIST = COMPARISON.left_list
		FOLDER_2_LIST = COMPARISON.right_list
		SAME_LIST = COMPARISON.common
		
		D1_FOLDERS = get_directories (FOLDER_1_LIST, FOLDER_1);
		D2_FOLDERS = get_directories (FOLDER_2_LIST, FOLDER_2);

		SAME_FOLDERS = get_same_directories (
			SAME_LIST, 
			FOLDER_1, 
			FOLDER_2
		);
		
		FOLDER_1_ONLY = COMPARISON.left_only
		FOLDER_2_ONLY = COMPARISON.right_only
		
		DIFFERENT_CONTENTS = COMPARISON.diff_files
		
		
		#
		#	FILES THAT ARE IN BOTH,
		#	BUT ARE NOT COMPARABLE.
		#
		#		? CHECKS PERMISSIONS?
		#
		INCOMPARABLE_FILES = COMPARISON.funny_files
		
		add_different_paths (
			proceeds,
		
			"1", 
			FOLDER_1, 
			FOLDER_1_ONLY, 
			REL_PREPEND = f"{ REL_PATH }/"
		)
		
		add_different_paths (
			proceeds,
		
			"2", 
			FOLDER_2, 
			FOLDER_2_ONLY, 
			REL_PREPEND = f"{ REL_PATH }/"
		)
		
		add_different_contents (
			proceeds,
		
			FOLDER_1, 
			DIFFERENT_CONTENTS,
			REL_PREPEND = f"{ REL_PATH }/"
		)
		
		for REL_PATH_ in SAME_FOLDERS:			
			FOLDERS = SAME_FOLDERS [ REL_PATH_ ]

			COMPARE_LEVEL (
				REL_PATH + "/" + REL_PATH_, 
				FOLDERS[0], 
				FOLDERS[1]
			)
	
		return;

	if (relative_paths == "no"):
		print ("????");
		
	else:
		add_different_paths (proceeds, "1", D1, D1_ONLY)
		add_different_paths (proceeds, "2", D2, D2_ONLY)

		add_different_contents (proceeds, D1, DIFFERENT_CONTENTS)

		for REL_PATH in SAME_FOLDERS:			
			FOLDERS = SAME_FOLDERS [ REL_PATH ]

			COMPARE_LEVEL (
				REL_PATH, 
				FOLDERS[0], 
				FOLDERS[1]
			)



		pass;


	return proceeds;
	
