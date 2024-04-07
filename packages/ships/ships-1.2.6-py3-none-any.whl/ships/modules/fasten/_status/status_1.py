


'''
	python3 status.py modules/fasten/_status/status_1.py
'''



import ships.modules.fasten._status.example_caller as example_caller


def check_1 ():
	returns = example_caller.start ()
	assert (returns == 500)

	
	
checks = {
	"fastener 1": check_1
}