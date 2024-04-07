




def awareness_EOF (p, journal):
	#print ("awareness_EOF", p)

	#
	#	https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
	#
	while (not p.eof () and p.isalive ()):
		print ('not eof', p.eof ())
	
		try:
			#print ('readline?')
			line = p.readline ()	
			#print ('line:', line)
			
			
			#print ('readline activated')
			
			try:
				UTF8_line = line.decode ('UTF8')
				UTF8_parsed = "yes"
			except Exception:
				UTF8_line = ""
				UTF8_parsed = "no"
				
			try:
				hexadecimal_line = line.hex ()
				hexadecimal_parsed = "yes"
			except Exception:
				hexadecimal_line = ""
				hexadecimal_parsed = "no"
			
			line_parsed = {
				"UTF8": {
					"parsed": UTF8_parsed,
					"line": UTF8_line
				},
				"hexadecimal": {
					"parsed": hexadecimal_parsed,
					"line": hexadecimal_line
				}
			};
			
			journal (line_parsed)

		except Exception as E:
			#print ("exception:", E)
			pass