

'''
	from ships.flow.simultaneous import simultaneously
	
	import time
	
	def move (item):
		print ("starting", item)
		
		time.sleep (item)
		result = f"Processed item: {item}"
		print (result)
		
		return result


	proceeds = simultaneously (
		items = [3.5, 1, 2, 1.1, 4, 1.11, 1.12, 1.13],
		capacity = 4,
		move = move
	)
'''


import threading
from queue import Queue
import time


def simultaneously (
	items = [],
	capacity = 2,
	move = lambda : None
):
	#
	#	capacity = 2
	#
	semaphore = threading.Semaphore (capacity)

	# Define a function to process items with semaphore limit and return results
	def process_with_semaphore (item, index, results_queue):
		with semaphore:
			result = move (item)
			results_queue.put((index, result))  # Put the result along with its index in the queue

	# Create a queue to collect the results
	results_queue = Queue ()

	# Create threads to process items
	threads = []
	for index, item in enumerate (items):
		thread = threading.Thread (target=process_with_semaphore, args=(item, index, results_queue))
		thread.start()
		threads.append(thread)

	# Wait for all threads to complete
	for thread in threads:
		thread.join()

	# Collect results from the queue and reorder them based on the original item order
	results = [None] * len(items)
	while not results_queue.empty():
		index, result = results_queue.get()
		results[index] = result
	
	return results;