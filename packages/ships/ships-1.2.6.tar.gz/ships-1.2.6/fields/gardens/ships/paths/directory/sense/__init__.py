
'''
	import ships.paths.directory.sense as sense

	def action (* pos, ** keys):
		return;

	sense.changes (
		directory = "",
		action = action
	)
'''

'''
import ships.cadence.filter as cadence_filter
CF = cadence_filter.start (
	every = 500
)

def action (is_delayed):
	return;

CF.attempt (
	action = action
)	
'''

import pyinotify

def action (* pos, ** keys):
	return;

def changes (
	directory = "",
	action = action
):
	wm = pyinotify.WatchManager ()

	class EventHandler (pyinotify.ProcessEvent):
		def process_IN_CREATE (self, event):
			print ("creation:", event.pathname)
			action ()

		def process_IN_DELETE (self, event):
			print ("removal:", event.pathname)
			action ()
			
		def process_default (self, event):
			if (
				event.maskname not in [
					"IN_OPEN",
					"IN_ACCESS",
					"IN_CLOSE_NOWRITE",
				
					"IN_OPEN|IN_ISDIR",
					"IN_ACCESS|IN_ISDIR",
					"IN_CLOSE_NOWRITE|IN_ISDIR",
				]			
			):
				print ("event:", event.maskname, event.pathname)
			#action ()

	handler = EventHandler ()
	notifier = pyinotify.Notifier (wm, handler)
	wdd = wm.add_watch (directory, pyinotify.ALL_EVENTS, rec = True)

	print ('Sensing for directory changes has started.');

	notifier.loop ()
