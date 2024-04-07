
'''
	priority:
	
		import ships.insure.equalities as equalities
		if (equalities.check ([
			[ 1, 1 ]
		])):	
'''


'''
		equalities.check ([
			[ 1, 1 ]
		], effect = "exception")
'''

def check (checks, effect = "", records = 1):
	index = 0
	for check in checks:
		if (check [0] != check [1]):		
			if (effect == "exception"):
				print ("check [0]:", check [0])
				print ("check [1]:", check [1])
				raise Exception (f'An inequality was found.')
			
			else:
				if (records >= 1):
					print ()
					print (f'An inequality was found at index:', index)
					print ("	check [0]:", check [0])
					print ("	check [1]:", check [1])
			
				return False
				
		index += 1
			
	return True