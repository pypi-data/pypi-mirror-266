
'''
import ships.ports.claimed as claimed
claimed_ports = claimed.find ()
'''

import psutil

def find (
	proceeds = "numbers"
):
	claimed = psutil.net_connections ()
	
	if (proceeds == "numbers"):
		revenue = []
	
		for claimed_port in claimed:
			#print ("claimed_port:", claimed_port.laddr.port)
			
			port = claimed_port.laddr.port
			assert (type (port) == int)
			
			revenue.append (port)
			
			
		#
		#	sorted returns a second sorted list
		#
		return sorted (revenue)
	
	return claimed;