

'''
	python3 status.py cycle/status_1.py
'''

import ships.cycle as cycle
import time

'''
	runs 3 times until gets positional param 1 == 3
'''
def check_1 ():
	orbits = 0

	def fn (* positionals, ** keywords):			
		assert (positionals [0] == 3)
		return 99 + positionals [0]
		
	returns = cycle.params (
		fn, 
		[
			[ 1 ],
			[ 2 ],
			[ 3 ]	
		],
		delay = 1
	)

	assert (returns == 102)

checks = {
	"check 1": check_1
}




#