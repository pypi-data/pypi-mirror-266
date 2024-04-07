

'''
	python3 status.py "flow/demux_mux/_status/status_1.py"
'''

import ships.flow.demux_mux as demux_mux

import time
import atexit
import shlex
import subprocess
	

def check_1 ():
	def circuit_1 (investments):
		def circuit ():
			print ('This is at the start of circuit 1.', investments)
			time.sleep (1)
			print ('This is near the end of circuit 1.', investments)
			
			assert (investments == 200000)

			return investments + 428937


		return circuit
		
	def circuit_2 (investments):
		def circuit ():
			print ('This is at the start of circuit 2.', investments)
			time.sleep (2)
			print ('This is near the end of circuit 2.', investments)

			assert (investments == 150000000)
			
			return investments + 129493001

		return circuit

	proceeds_statement = demux_mux.start ([
		circuit_1 (200000),
		circuit_2 (150000000)
	])
	
	print ("demux_mux proceed statement received")
	print (proceeds_statement)
	
	assert (proceeds_statement [0] == 628937)
	assert (proceeds_statement [1] == 279493001)
		
	
	return;
	
checks = {
	"check 1": check_1
}