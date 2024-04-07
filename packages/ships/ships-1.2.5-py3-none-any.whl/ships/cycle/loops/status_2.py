

'''
	python3 status.py 'cycle/**/status_*.py'
	python3 status.proc.py 'cycle/loops/status_2.py'
'''

import ships.cycle as cycle
import time
from fractions import Fraction

def check_1 ():
	request_worked = 0

	def fn (* positionals, ** keywords):
		print ("cycling", positionals, keywords)
	
		assert (positionals [0] == 1)
		assert (len (positionals) == 1)
		assert (len (keywords) == 0)

		nonlocal request_worked;
		request_worked += 1

		assert (request_worked == 10)		
	
		return 99
		
	returns = cycle.loops (
		fn, 
		cycle.presents ([ 1 ]),
		
		loops = 10,
		delay = Fraction (1, 4),
		
		records = 1
	)

	assert (returns == 99)
	assert (request_worked == 10)

checks = {
	"check 1": check_1
}




#