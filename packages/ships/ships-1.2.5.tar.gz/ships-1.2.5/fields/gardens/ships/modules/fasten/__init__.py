

'''
import ships.modules.fasten as fasten
vehicle = fasten.module ("/structures/thruster.py")
vehicle.start ()

#
#	thruster.py
#
#	def start ():
#		print ('start')
#

'''

from importlib.machinery import SourceFileLoader
import inspect
import os

	
def module (module_path):	
	if (module_path [ 0 ] == "/"):
		full_path = module_path;
		
	else:
		file_of_caller_function = os.path.abspath (
			(inspect.stack () [1]) [1]
		)
		directory_of_caller_function = os.path.dirname (
			file_of_caller_function
		)	
		
		#print ("directory_of_caller_function:", directory_of_caller_function)
		#print ("inspect.stack ():", inspect.stack ())

		#dir_path = os.path.dirname (os.path.realpath (__file__))
		full_path = os.path.normpath (directory_of_caller_function + "/" + module_path)


	return SourceFileLoader (full_path, full_path).load_module ()

