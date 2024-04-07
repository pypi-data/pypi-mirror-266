

'''
	import ships.cycle.UTC.month.strings as UTC_month_strings
	UTC_month_strings.learn (12)
'''

'''
	months 1 TO 12
'''


def learn (integer = False):
	month_strings = [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December"
	]
	
	if (integer == False):
		return month_strings

	assert (type (integer) == int)
	return month_strings [ integer - 1]