
'''
	python3 status.py "ports/_status/status_1.py"
'''

import ships.ports.available as available_port
import ships.ports.claimed as claimed
	
def check_1 ():
	claimed_ports = claimed.find ()
	
	#for claimed_port in claimed_ports:
	#	print ("claimed_port:", type (claimed_port), claimed_port)
	
	port = available_port.find ()
	available = available_port.check (port)

	assert (type (claimed_ports) == list)
	assert (type (port) == int)
	assert (available == True)
	
	return;
	
	
checks = {
	"1": check_1 
}