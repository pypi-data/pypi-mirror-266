








"""
	import ships.process.multi as multiproc
	
	multiprocs = multiproc.start (
		processes = [
			{ 
				"string": 'python3 -m http.server 9000',
				"Popen": {
					"cwd": None
				}
			},
			{
				"string": 'python3 -m http.server 9001',
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

	time.sleep (.5)
	
	
	#
	#	stop
	#
	multiprocs.stop ()
"""


from subprocess import Popen
import shlex
import atexit

def start (
	processes = [],
	wait = False
):
	processes_list = []

	for process in processes:
		if (type (process) == str):	
			routine = Popen (shlex.split (process_string))
			
			print ('routine:', routine)
			
			processes_list.append (routine)
			
		elif (type (process) == dict):		
			process_string = process ["string"]
		
			cwd = None
			env = None
		
			args = {}
			if ("Popen" in process):
				args = process ["Popen"]

			
			this_process_Popen = Popen (
				shlex.split (process_string),
				** args
			)

			print ('this_process_Popen:', this_process_Popen)

			processes_list.append (this_process_Popen)

	
	def stop ():
		for process in processes_list:
			process.kill ()

	'''
		This might only work if this is called:
			process.wait () 
	'''
	print ("registering atexit stop")	
	atexit.register (stop)
	
	if (wait):
		for process in processes_list:
			#
			#	https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait
			#
			process.wait ()	
	
	
	class returns:
		def __init__ (this, processes):
			this.processes = processes
			
		def stop (this):
			print ("stop called")
		
			stop ()
			
	this_returns = returns (
		processes = processes_list
	)
	
	print (this_returns)
	
	return this_returns

	
	
	


