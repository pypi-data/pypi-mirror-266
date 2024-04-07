

'''
	python3 status.py "process/multi/_status/status_1.py"
'''

import ships.process.multi as multiproc
import time
import atexit
import shlex
import subprocess
	
def attempt (fn, params, delay, loop = 0):
	these_params = params [ loop ]
	
	try:
		fn (* these_params)
	except Exception as E:
		print ("Exception:", E)

		if (loop <= (len (params) - 1)):
			attempt (fn, params, delay, loop = loop + 1)

	return;

def check_1 ():
	return;

	process_1 = subprocess.Popen (shlex.split ("python3 -m http.server 9000"))
	process_1.kill ()
	
	def process_2 (port):
		print ("starting process 2 on port:", port)
	
		process_2 = subprocess.Popen (shlex.split (f"python3 -m http.server { port }"))

		print ("process_2:", process_2)
		process_2.kill ()
	
	attempt (
		process_2,
		[ 
			[ "9001" ]
		],
		100
	)

	return;
	
	
checks = {
	"check 1": check_1
}