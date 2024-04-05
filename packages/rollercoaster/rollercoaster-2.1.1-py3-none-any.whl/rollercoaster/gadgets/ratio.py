






'''
	from rollercoaster.tools.ratio import calculate_ratio
'''

def calculate_ratio (s1, s2):
	if (s1 == 0 or s2 == 0):
		return [ "?", "?" ]
		#return "can't divide by zero"
		
		#return [ "~ >= infinity", 0 ]
		#return [ "infinity", 1 ]

	if (s1 == s2):
		return [ 1, 1 ]
	
	elif (s1 >= s2):
		return [
			s1 / s2,
			1
		]
	
	elif (s2 >= s1):
		return [
			1,
			s2 / s1
		]
	
	
	raise ("?")
