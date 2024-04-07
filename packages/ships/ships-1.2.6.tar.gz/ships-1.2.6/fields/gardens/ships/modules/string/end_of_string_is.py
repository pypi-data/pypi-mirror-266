




'''
	This checks if a partial string
	is at the end of another string.
'''
def end_of_string_is (string, partial):
	try:
		index = string.index (partial)
		if (len (string) == (index + len (partial)):
			return True
			
	except Exception:
		pass

	return False