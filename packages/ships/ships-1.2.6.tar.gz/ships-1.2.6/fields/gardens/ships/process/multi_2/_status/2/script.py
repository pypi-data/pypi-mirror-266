




import time

episode = 1
def step ():
	global episode;

	print ('step', episode)
	#print (b'asdf')
	
	episode += 1
	
	time.sleep (1)
	
	if (episode <= 3):	
		step ()
	
step ()