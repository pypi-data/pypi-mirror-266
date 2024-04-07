

'''
	python3 status.py 'cycle/status_4.py'
'''

import ships.cycle as cycle
import time
from fractions import Fraction

def check_1 ():
	loop_number = 0

	def fn (* positionals, ** keywords):
		print ("fn called")
	
		nonlocal loop_number;
		loop_number += 1
	
		raise Exception ("yes")
	
	exception_string = ""
	try:
		returns = cycle.loops (
			fn, 
			cycle.presents ([ 1 ]),
			
			loops = 5,
			delay = Fraction (1, 4),
			
			records = 1
		)
		print ("returns:", returns)
		
	except Exception as e:
		exception_string = str (e);

	
	print ("exception_string:", exception_string)
	

	assert (exception_string == "The loop limit was reached.")
	assert (loop_number == 5)

checks = {
	"check 1": check_1
}




#