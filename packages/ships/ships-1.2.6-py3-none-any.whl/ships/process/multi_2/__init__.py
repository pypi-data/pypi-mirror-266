

'''
	calendar:
		[ ] output recorder
		[ ] coverage
		[ ] start in background
'''	


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

import rich
import pexpect

from subprocess import Popen
import shlex
import atexit
import asyncio

import ships.flow.demux_mux2 as demux_mux2

import multiprocessing
import threading
import time		

def awareness_EOF (p, journal):
	print ("awareness_EOF", p)

	while (not p.eof () and p.isalive ()):
		try:
			line = p.readline ()	
			
			#print ('readline activated')
			
			try:
				UTF8_line = line.decode ('UTF8')
				UTF8_parsed = "yes"
			except Exception:
				UTF8_line = ""
				UTF8_parsed = "no"
				
			try:
				hexadecimal_line = line.hex ()
				hexadecimal_parsed = "yes"
			except Exception:
				hexadecimal_line = ""
				hexadecimal_parsed = "no"
			
			line_parsed = {
				"UTF8": {
					"parsed": UTF8_parsed,
					"line": UTF8_line
				},
				"hexadecimal": {
					"parsed": hexadecimal_parsed,
					"line": hexadecimal_line
				}
			};
			
			journal (line_parsed)

			#rich.print_json (data = line_parsed)
		except Exception as E:
			print ("exception:", E)
			pass

def start (
	processes = [],
	wait = False
):
	processes_list = []

	for process in processes:
		if (type (process) == str):	
			routine = Popen (shlex.split (process_string))
			
			#print ('routine:', routine)
			
			processes_list.append (routine)
			
		elif (type (process) == dict):		
			process_string = process ["string"]
		
			cwd = None
			env = None
		
			args = {}
			if ("Popen" in process):
				args = process ["Popen"]

			#
			#	a noop
			#
			journal = lambda *args, **kwargs: None
			if ("journal" in process):
				journal = process ["journal"]


			
			'''
			p = pexpect.popen_spawn.PopenSpawn (
				process_string,
				** args
			)
			'''
			
			this_process = pexpect.spawn (
				process_string,
				** args
			)
			
			'''
			from multiprocessing import Process
			p = Process (
				target = awareness_EOF,
				args = (this_process, journal)
			)
			p.start ()
			#p.join ()
			'''
			
			
			from threading import Thread
			p = Thread (
				target = awareness_EOF,
				args = (this_process, journal)
			)
			p.start ()
			#p.join ()
			
			
			'''
			class MyThread (threading.Thread):
				def run (self):
					awareness_EOF (this_process, journal)

			# create and start the thread
			t = MyThread ()
			t.start ()
			print ('after', t)
			'''

			

			

			
			'''
			proceeds_statement = demux_mux2.start (
				course, 
				[ 1 ]
			)	
			'''
				
			print ("after demux")
				
			
			'''
			this_process_Popen = Popen (
				shlex.split (process_string),
				** args
			)
			'''

			#print ('this_process_Popen:', p)

			processes_list.append (this_process)
			
	print ("yep")

	
	def stop ():
		print ('stopping')
	
		for process in processes_list:
			process.close ()


	'''
		This might only work if this is called:
			process.wait () 
	'''
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

	
	
	


