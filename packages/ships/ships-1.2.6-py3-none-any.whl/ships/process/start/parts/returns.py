

class returns:
	def __init__ (this, process):
		this.process = process
		
	def stop (this):
		this.process.close ()

'''
class returns:
	def __init__ (this, process, coverage, coverage_dir):
		this.process = process
		this.cov = coverage
		this.coverage_dir = coverage_dir
		
	def stop (this):
		coverage_dir = this.coverage_dir;
	
		this.cov.stop ()
		this.cov.save ()
		
		if (type (coverage_dir) == str):
			cov.html_report (directory = coverage_dir)
		
		this.process.close ()
'''