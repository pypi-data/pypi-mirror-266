


'''
	python3 status.py 'cadence/filter/_status/status_1.py'
'''

import time

from fractions import Fraction

def check_1 ():
	import ships.cadence.filter as cadence_filter
	CF = cadence_filter.start (
		every = Fraction (1,2)
	)
	
	
	sequence = []

	def action (is_delayed, parameters):
		print ()
		print ("	action: is_delayed:", is_delayed)
		print ()

		sequence.append (is_delayed)

		return;

	CF.attempt (action = action)

	assert (
		sequence == [
			False
		]
	), sequence

	return;


	
	
checks = {
	'check 1': check_1
}