
'''
	from ships.cycle.presents import presents as cycle_presents
'''

'''
	cycle_presents ([])
	cycle_presents ([], {})
'''
class presents:
	def __init__ (this, * positionals):
		this.positionals = positionals [0]
		
		if (len (positionals) >= 2):
			this.keywords = positionals [1]
		else:
			this.keywords = {}