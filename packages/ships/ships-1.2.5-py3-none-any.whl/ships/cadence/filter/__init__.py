

'''
	priorities:
		
	
		import ships.cadence.filter as cadence_filter
		CF = cadence_filter.start (every = 1)

		def action (is_delayed, parameters):
			return;

		CF.attempt (
			action = action,
			parameters = [ 1 ]
		)		
'''

from threading import Timer, Thread
import threading
from concurrent.futures.thread import ThreadPoolExecutor

import asyncio

import time

def action (is_delayed):
	return;

def start (
	every = 1
):
	every = float (every)

	class CF:
		is_filtering = False
		next_action = action
	
		stop_watch = False
	
		def __init__ (this):
			return;
			
		def background_sleep (this):
			print ('background sleep started')
		
			def sleep_thread ():
				time.sleep (every + 1)
				print ('background sleep ended')
		
			t = Thread (target = sleep_thread)
			t.start ()
			t.join ()
			
		def stop_timer ():
			
		
			return;
		
		def start_timer (this):		
			def timer_action ():
				print ('timer action?')
				this.next_action (
					is_delayed = True, 
					parameters = this.parameters
				)
		
				this.is_filtering = False;
		
			
			this.stop_watch = Timer (
				every, 
				timer_action
			)
			
			this.stop_watch.start ()
			print ("timer started:", every)
			
			#this.stop_watch.join ()
			
			#time.sleep (float (every) + 1)
		
		
		'''
			if is_filtering:
				then 
				
			else:
				
		'''
		def attempt (this, action, parameters = []):
			print ("is_filtering:", this.is_filtering)
			
			if (this.is_filtering == False):
				this.is_filtering = True;
				
				action (
					is_delayed = False,
					parameters = parameters
				);
				
				
				
				'''
				print ("timer started")
				
				t = Timer (2000, action)
				t.start ()
				
				#this.start_timer ()
				'''
				
			else:
				if (type (this.stop_watch) == Timer):
					print ('cancelling stop watch')
					this.stop_watch.cancel ()
					
				this.next_action = action;
				this.parameters = parameters
				
				
				this.start_timer ()
				

			
			
			return;
			
	
	this_CF = CF ();
	
	
	return this_CF
