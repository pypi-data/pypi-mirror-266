
'''
	this only sends positional arguments
'''

'''
def fn (* positionals, ** keywords):			
	assert (positionals [0] == 3)
	return 99 + positionals [0]
	
returns = cycle.params (
	fn, 
	[
		#
		#	loop 1
		#
		[ 1 ],
		
		#
		#	loop 2
		#
		[ 2 ],
		
		#
		#	loop 3
		#
		[ 3 ]	
	],
	delay = 1
)

assert (returns == 102)
'''

import time

def start (
	fn, 
	fn_params, 
	
	delay = 1, 
	loop = 0,
	records = 1
):
	try:
		return fn (* fn_params [ loop ]);			
	except Exception as E:
		if (records >= 1):
			print ("cycle didn't work.", E)

	time.sleep (delay)
	
	return start (
		fn, 
		fn_params, 
		
		delay = delay,
		loop = loop + 1,
		records = records
	)
