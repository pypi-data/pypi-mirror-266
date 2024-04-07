

'''
import ships.flow.demux_mux as demux_mux

def circuit_1 (investments):
	def circuit ():
		print (investments)

	return circuit
	
def circuit_2 (investments):
	def circuit ():
		print (investments)

	return circuit

proceeds_statement = demux_mux.start ([
	circuit_1 (200000),
	circuit_2 (150000000)
])
'''

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def start (circuits):

	proceeds_statement = []

	#def component (circuit):
	#	circuit ()

	with ThreadPoolExecutor () as TPE:
		proceeds = TPE.map (
			lambda circuit : circuit (), 
			circuits
		)
		
		TPE.shutdown (wait = True)
		
		for proceed in proceeds:
			proceeds_statement.append (proceed)

	return proceeds_statement
	
	





def now (
	finds,
	module_paths,
	relative_path,
	records
):
	OUTPUT = []

	def FN (path):
		[ status ] = scan.start (		
			path = path,
			module_paths = module_paths,
			relative_path = relative_path,
			records = records
		)
	
		return status;
	
	
	with ThreadPoolExecutor () as executor:
		RETURNS = executor.map (
			FN, 
			finds
		)
		
		executor.shutdown (wait = True)
		
		for RETURN in RETURNS:
			OUTPUT.append (RETURN)
			
		
	return OUTPUT;