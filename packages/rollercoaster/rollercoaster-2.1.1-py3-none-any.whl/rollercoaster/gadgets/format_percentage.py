



'''
	from calc.format_percentage import format_percentage
	PERCENTAGE = format_percentage (.1239)
'''

'''
	STRING PERCENTAGE: "###.#%"
'''
def format_percentage (DECIMAL):
	DECIMAL = DECIMAL * 100;

	try:
		if (DECIMAL > 100):
			return " >100%"

		SPLIT = str (DECIMAL).split (".")
		
		if (len (SPLIT[0]) == 0):
			SPLIT[0] = " 00"
			
		elif (len (SPLIT[0]) == 1):
			SPLIT[0] = " 0" + SPLIT[0]
			
		elif (len (SPLIT[0]) == 2):
			SPLIT[0] = " " + SPLIT[0]
			
		PERCENTAGE = SPLIT[0] + "." + SPLIT[1][0] + SPLIT[1][1] + "%"
		
		return PERCENTAGE;
		
	except Exception as E:
		print (E)
		
	return "???.?%"
	
	