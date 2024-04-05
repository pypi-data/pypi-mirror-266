


'''
	agenda:
		from rollercoaster.gadgets.summation import summation
	
		def formula (s):
			return;
	
		summation (
			start = 1,
			end = 75,
			formula = formula
		)
'''

def formula (s):
	return;

def summation (
	start = None,
	end = None,
	formula = formula
):
	assert (type (start) == int)
	assert (type (end) == int)
	
	proceeds = 0
	
	current = start
	while (current <= end):
		proceeds += formula (current)
	
		current += 1
	

	return proceeds
