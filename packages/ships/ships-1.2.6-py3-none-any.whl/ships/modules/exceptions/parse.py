
'''
import ships.modules.exceptions.parse as parse_exception
print (parse_exception.now (exception))
'''

'''
import ships.modules.exceptions.parse as parse_exception

try:
	variable = 1 + "1"
except Exception as E:
	print (parse_exception.now (E))
'''

import io
import sys
import traceback

def now (exception : Exception) -> str:
	file = io.StringIO ()
	traceback.print_exception (exception, file = file)
	
	return file.getvalue ().rstrip ()