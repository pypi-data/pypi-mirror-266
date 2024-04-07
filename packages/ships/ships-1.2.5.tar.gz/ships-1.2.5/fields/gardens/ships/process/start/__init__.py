

'''
	calendar:
		[ ] output recorder
		[ ] coverage
		[ ] start in background
'''	


"""
	import ships.process.start as process_starter
	
	multiprocs = process_starter.start (
		process = { 
			"string": 'python3 -m http.server 9000',
			"Popen": {
				"cwd": None
			}
		},
		
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
#import pexpect

import ships.pexpect_4_9_0_copy as pexpect


import coverage

from subprocess import Popen
import shlex
import atexit
import asyncio

import ships.flow.demux_mux2 as demux_mux2

import multiprocessing
import threading
import time		
from threading import Thread

from .parts.awareness import awareness_EOF
from .parts.returns import returns

def start (
	process = {},
	wait = False
):
	processes_list = []

	#print ('coverage?')

	#cov = coverage.Coverage (data_file = coverage_data_file)
	#cov.start ()

	
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

	the_process = pexpect.spawn (
		process_string,
		** args
	)


	p = Thread (
		target = awareness_EOF,
		args = (the_process, journal)
	)
	p.start ()
	

	this_returns = returns (
		process = the_process
	)

	'''
		This might only work if this is called:
			process.wait () 
	'''
	atexit.register (this_returns.stop)
	
	if (wait):
		the_process.wait ()	

	
	return this_returns

	
	
	


