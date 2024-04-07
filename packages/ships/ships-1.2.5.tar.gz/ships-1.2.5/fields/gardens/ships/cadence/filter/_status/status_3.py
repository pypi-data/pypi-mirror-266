





'''
	python3 status.py 'cadence/filter/_status/status_3.py'
'''

import time

from fractions import Fraction
from threading import Timer, Thread

def check_1 ():

	import ships.cadence.filter as cadence_filter
	CF = cadence_filter.start (
		every = Fraction (1,1)
	)
	
	sequence = []

	def action (
		is_delayed, 
		parameters
	):
		
		print ()
		print ("	action: is_delayed:", is_delayed)
		print ("	action: positionals:", parameters)
		print ()
		
		sequence.append ([ parameters [0], is_delayed ])
		
		return;

	CF.attempt (action = action, parameters = [ 1 ])
	CF.attempt (action = action, parameters = [ 2 ])
	CF.attempt (action = action, parameters = [ 3 ])
	
	time.sleep (2)
	
	CF.attempt (action = action, parameters = [ 4 ])
	
	time.sleep (1)
	
	assert (
		sequence == [
			[ 1, False ],
			[ 3, True ],
			[ 4, False ]
		]
	), sequence
	
	
	
	
	#time.sleep (1)
	#CF.attempt (action = action)
	
	
	

	return;
	
	
checks = {
	'check 1': check_1
}