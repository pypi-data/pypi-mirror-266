



'''
"DATE": 
	{
		"CALENDAR": "UTC",
		
		"YEAR": [ 1983, "-INFINITY TO -1, 1 TO INFINITY" ],
		"MONTH": [ "AUGUST", "JANUARY TO DECEMBER" ],
		"DAY OF MONTH": [ 24, "1 TO __" ],
		
		"HOUR": [ 18, "0 TO 23" ],
		"MINUTE": [ 49, "0 TO 59" ]
	},
'''

import datetime
from datetime import datetime, timezone

import ships.cadence.UTC.month.strings as UTC_month_strings
	

def learn ():
	#current = datetime.datetime.utcnow ()
	current = datetime.now (timezone.utc)

	'''
	print (current)
	print (current.year)
	print (current.month)
	print (current.day)
	
	#
	#	00:00 TO 23:59
	#
	print (current.hour)
	'''

	return {
		"calendar": "UTC+00:00",
		
		"year": [ 
			current.year, 
			"-INFINITY TO -1, 1 TO INFINITY" 
		],
		
		"month": [ 
			UTC_month_strings.learn (current.month), 
			"January to December" 
		],
		
		"day of month": [ 
			current.day, "1 to __" 
		],
		
		"hour": [ current.hour, "0 to 23" ],
		"minute": [ current.minute, "0 to 59" ]
	}