
'''
	if cycling, then limit can be reduced each time,
		[ 10000, 60000 ]
		[ 10001, 60000 ]
		[ 10002, 60000 ]

	until, for example 
'''

'''
	import ships.ports.available as available_port
	port = available_port.find (
		limits = [ 10000, 60000 ]
	)
'''


'''
	import ships.ports.available as available_port
	available = available_port.check (10000)
'''

import socket

import ships.ports.claimed as claimed



def check (port):
	claimed_ports = claimed.find ()
	if (port not in claimed_ports):
		return True
	
	return False
#
#	
#
def find (
	limits = [ 10000, 60000 ]
):
	check = limits [0]
	claimed_ports = claimed.find ()
	
	limit_end = limits [1]
	
	while (check <= limit_end):
		if (check not in claimed_ports):
			return check
			
		check += 1

	return;


#
#	this is probably random
#		https://stackoverflow.com/a/36331860/2600905
#
def find_v1 ():
    with socket.socket () as this_socket:
        this_socket.bind (('', 0))
        return this_socket.getsockname () [1]

