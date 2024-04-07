






'''
	python3 status.proc.py "process/start/_status/status_1.py"
'''

import time



import rich

import ships.process.start as process_starter

def CWD ():
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_folder = pathlib.Path (__file__).parent.resolve ()	
	return str (this_folder)


def check_1 ():
	import pathlib
	from os.path import dirname, join, normpath
	import sys

	journal_1_list = []
	def journal_1 (line_parsed):
		journal_1_list.append (line_parsed)

	port = "9004"

	the_process = process_starter.start (	
		process = { 
			"string": f'python3 -m http.server { port }',
			"Popen": {
				"cwd": None
			},
			"journal": journal_1
		},
		
		#
		#	True -> wait for "ctrl and c"
		#
		wait = False
	)
	
	time.sleep (.5)

	print ("started server?")

	import json
	from os.path import dirname, join, normpath
	import os
	import requests
	r = requests.get (
		f'http://127.0.0.1:{ port }', 
		data = json.dumps ({})
	)
	assert (r.status_code == 200), r.status_code
	
	print ('got status?')
	
	
	#
	#	stop
	#
	the_process.stop ()
	
	
	rich.print_json (data = journal_1_list)


	return;
	
	
checks = {
	"check 1": check_1
}