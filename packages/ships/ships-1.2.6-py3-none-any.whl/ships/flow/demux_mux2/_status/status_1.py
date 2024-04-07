




'''
	python3 status.py "flow/demux_mux2/_status/status_1.py"
'''

import ships.flow.demux_mux2 as demux_mux2

import time
import atexit
import shlex
import subprocess
	

def check_1 ():
	def course (parameter):
		print ("course:", parameter)
		
		return parameter + 10


	proceeds_merger = demux_mux2.start (
		course, 
		[ 
			1, 
			2,
			11,
			9
		]
	)
	
	assert (
		proceeds_merger ==
		[
			11, 
			12,
			21,
			19
		]
	)
	
	print ("proceeds_merger:", proceeds_merger)
	
checks = {
	"check 1": check_1
}