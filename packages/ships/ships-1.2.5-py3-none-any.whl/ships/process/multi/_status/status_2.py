



'''
	python3 status.proc.py "process/multi/_status/status_2.py"
'''

import time


def check_1 ():
	import ships.process.multi as multiproc
	multiprocs = multiproc.start (
		processes = [
			{ 
				"string": 'python3 -m http.server 9001',
				"Popen": {
					"cwd": None
				}
			},
			{
				"string": 'python3 -m http.server 9002',
				"Popen": {
					"cwd": None
				}
			}
		],
		
		#
		#	True -> wait for "ctrl and c"
		#
		wait = False
	)
	
	processes = multiprocs.processes

	time.sleep (2.5)
	

	import json
	from os.path import dirname, join, normpath
	import os
	import requests
	r = requests.get (
		'http://127.0.0.1:9001', 
		data = json.dumps ({})
	)
	assert (r.status_code == 200), r.status_code
	
	
	r = requests.get (
		'http://127.0.0.1:9002', 
		data = json.dumps ({})
	)
	assert (r.status_code == 200), r.status_code
	
	#
	#	stop
	#
	multiprocs.stop ()


	return;
	
	
checks = {
	"check 1": check_1
}