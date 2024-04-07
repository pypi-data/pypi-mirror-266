
'''
action 1 <function action_2 at 0x7facdc649440>
clock <function action_1.<locals>.inner at 0x7facdc6494e0>
clock 1 inner <function action_1.<locals>.inner at 0x7facdc6494e0>
action 1 inner <function action_2 at 0x7facdc649440>
clock elapsed: 5.245208740234375e-06

'''

def action_1 (function):
	print ("action 1", function)
	
	def inner ():
		print ("action 1 inner", function)
	
	
	return inner
	
import time
def clock (function):
	print ("clock", function)
	
	def inner ():
		t1 = time.time ()
		
		print ("clock 1 inner", function)
		proceeds = function ()
		
		t2 = time.time ()
		elapsed = t2 - t1
		
		print ("clock elapsed:", elapsed)
	
	
	return inner	
	
@clock
@action_1
def action_2 ():
	print ("action 2")
	return;
	
	
action_2 ();