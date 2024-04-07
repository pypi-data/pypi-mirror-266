




'''
	python3 status.proc.py cycle/params_2/status_1.py
'''


import ships.cycle.params_2 as cycle_params_2
from ships.cycle.presents import presents as cycle_presents

import time

'''
	runs 3 times until gets positional param 1 == 3
'''
def check_1 ():
	orbits = 0
	

	arguments = []	
	
	def fn (* positionals, ** keywords):	
		print (positionals, keywords)
	
		arguments.append ([ list (positionals), keywords ])
	
		assert (positionals [0] == 3)
		return 99 + positionals [0]
		
	returns = cycle_params_2.start (
		fn, 
		[
			cycle_presents ([ 1 ], { "1": 1 }),
			cycle_presents ([ 2 ], { "2": 2 }),
			cycle_presents ([ 3 ], { "3": 4 })	
		],
		delay = .5
	)

	print (arguments)

	assert (
		arguments ==
		[
			[[1], {'1': 1}], 
			[[2], {'2': 2}], 
			[[3], {'3': 4}]
		]
	)

	assert (returns == 102)

checks = {
	"check 1": check_1
}




#