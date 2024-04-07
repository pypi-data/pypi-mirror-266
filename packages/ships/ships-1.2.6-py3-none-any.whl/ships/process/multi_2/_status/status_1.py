






'''
	python3 status.proc.py "process/multi_2/_status/status_1.py"
'''

import time
import rich

def check_1 ():

	journal_1_list = []
	def journal_1 (line_parsed):
		rich.print_json (data = line_parsed)
		journal_1_list.append (line_parsed)
	
	port = "9003"

	import ships.process.multi_2 as multiproc_2
	multiprocs = multiproc_2.start (
		processes = [
			{ 
				"string": f'python3 -m http.server { port }',
				"Popen": {
					"cwd": None
				},
				"journal": journal_1
			}
		],
		
		#
		#	True -> wait for "ctrl and c"
		#
		wait = False
	)
	
	#print ('after wait')
	
	processes = multiprocs.processes

	time.sleep (.5)
	

	import json
	from os.path import dirname, join, normpath
	import os
	import requests
	r = requests.get (
		f'http://127.0.0.1:{ port }', 
		data = json.dumps ({})
	)
	assert (r.status_code == 200), r.status_code

	
	#
	#	stop
	#
	multiprocs.stop ()
	
	
	print ("journal 1 list")
	rich.print_json (data = journal_1_list)
	

	return;
	
	
checks = {
	"check 1": check_1
}