




import time

episode = 1
def step ():
	global episode;

	print ('step', episode)
	
	time.sleep (1)
	
	episode += 1
	if (episode <= 3):	
		step ()
	
step ()