


'''
	priorities:
		import ships.flow.demux_mux2 as demux_mux2

		def course (investments):
			print (investments)


		proceeds_statement = demux_mux2.start (
			course, 
			[]
		)
'''

'''
	Description:
		order of inputs == order of outpus
		
		one exception 
'''

'''
	https://stackoverflow.com/questions/16276423/pythons-concurrent-futures-iterate-on-futures-according-to-order-of-completi?rq=4
'''

'''
	https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
'''

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import concurrent.futures
import time
	
def start (course, batches):
	proceeds_merger = []
	with concurrent.futures.ThreadPoolExecutor (max_workers = 3) as TPE:		
		proceeds_merger = (
			list (
				TPE.map (course, batches)
			)
		)

	return proceeds_merger;