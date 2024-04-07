
'''
	import ships.ports.find_multiple as find_multiple_ports
	ports = find_multiple_ports.beautifully (
		limits = [ 10000, 60000 ],
		amount = 10
	)
'''
	
import ships.ports.available as available_port

def beautifully (
	limits = [ 10000, 60000 ],
	amount = 1
):
	ports = []
	port = available_port.find (
		limits = limits
	)
	ports.append (port)

	amount_minus_1 = amount - 1;
	while (len (ports) <= amount_minus_1):
		last_port = ports [ len (ports) - 1 ]
	
		next_port = last_port + 1;
		while (True):
			if (available_port.check (next_port)):
				ports.append (next_port);
				break;
				
			next_port += 1
	
	return ports
	