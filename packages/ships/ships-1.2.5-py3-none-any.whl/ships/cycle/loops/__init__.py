
'''
	Description:
		This function calls the show function 
		until either:
			
			the loop limit is reached
			the "show" function doesn't raise an exception			


	loop with the same parameters, each cycle
'''

'''

import ships.cycle.loops as cycle_loops

def show (* positionals, ** keywords):
	print (positionals)
	print (keywords)

	return 99
	
proceeds = cycle_loops.start (
	show, 
	cycle.presents ([ 1 ]),
	
	#
	#	this is the loop limit
	#
	loops = 10,
	delay = Fraction (1, 4)
)
'''


import time
import ships.modules.exceptions.parse as parse_exception
'''

'''
def start (
	* positionals, 
	** keywords
):
	#print ("loops called")

	fn = positionals [0]
	fn_presents = positionals [1] 
	
	this_loops = keywords ["loops"],
	
	if ("loops" in keywords):
		this_loops = keywords ["loops"]
	else:
		this_loops = 1
	
	if ("delay" in keywords):
		this_delay = keywords ["delay"]
	else:
		this_delay = 1
		
	if ("records" in keywords):
		this_records = keywords ["records"]
	else:
		this_records = 0
		
	if ("loop_number" in keywords):
		this_loop_number = keywords ["loop_number"]
	else:
		this_loop_number = 1
		
	if (this_loop_number > this_loops):
		raise Exception (f"The loop limit was reached.")

	if (this_records >= 1):
		print ("at loop number ", this_loop_number, "of", this_loops)

	'''
		try the function,
			if it doesn't work 
	'''
	try:
		return fn (
			* fn_presents.positionals,
			** fn_presents.keywords
		);			
	except Exception as E:
		if (this_records >= 1):		
			print (
				"cycle didn't work, received exception", 
				parse_exception.now (E)
			)

	time.sleep (float (this_delay))
	
	keywords ["loop_number"] = this_loop_number + 1
	
	return start (
		* positionals, 
		** keywords
	)
	