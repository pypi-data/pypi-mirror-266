






'''
	python3 status.proc.py "process/multi_2/_status/2/status_2.py"
'''

import time
import rich
import ships.process.multi_2 as multiproc_2

import pathlib
from os.path import dirname, join, normpath
import sys

def CWD ():
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_folder = pathlib.Path (__file__).parent.resolve ()	
	return str (this_folder)

def check_1 ():

	journal_1_list = []
	def journal_1 (line_parsed):
		rich.print_json (data = line_parsed)
		journal_1_list.append (line_parsed)

	
	multiprocs = multiproc_2.start (
		processes = [
			{ 
				"string": 'python3 script.py',
				"Popen": {
					"cwd": CWD ()
				},
				"journal": journal_1
			}
		],
		
		#
		#	True -> wait for "ctrl and c"
		#
		wait = True
	)


	assert (
		journal_1_list [0] ==
		{
		"UTF8": {
		"parsed": "yes",
		"line": "step 1\r\n"
		},
		"hexadecimal": {
		"parsed": "yes",
		"line": "7374657020310d0a"
		}
		}
	)
	
	assert (
		journal_1_list [1] ==
		  {
			"UTF8": {
			  "parsed": "yes",
			  "line": "step 2\r\n"
			},
			"hexadecimal": {
			  "parsed": "yes",
			  "line": "7374657020320d0a"
			}
		  }
		)
		
	assert (
		journal_1_list [2] ==
		  {
			"UTF8": {
			  "parsed": "yes",
			  "line": "step 3\r\n"
			},
			"hexadecimal": {
			  "parsed": "yes",
			  "line": "7374657020330d0a"
			}
		  }
	)
	
	assert (len (journal_1_list) >= 3)
	


	return;
	
	
checks = {
	"check 1": check_1
}