


import ships.cadence.UTC.current as UTC_current
import ships.cadence.UTC.month.strings as UTC_month_strings

def check_1 ():
	current_UTC = UTC_current.learn ()
	
	import json
	print (json.dumps (current_UTC, indent = 2))

	assert (current_UTC ["calendar"] == 'UTC+00:00')
	assert (current_UTC ["year"][0] >= 1500)
	assert (current_UTC ["month"][0] in UTC_month_strings.learn ())

	assert (current_UTC ["day of month"][0] >= 1)
	assert (current_UTC ["day of month"][0] <= 31)
	
	assert (current_UTC ["hour"][0] >= 0)
	assert (current_UTC ["hour"][0] <= 23)

	return;
	
checks = {
	"check 1": check_1
}