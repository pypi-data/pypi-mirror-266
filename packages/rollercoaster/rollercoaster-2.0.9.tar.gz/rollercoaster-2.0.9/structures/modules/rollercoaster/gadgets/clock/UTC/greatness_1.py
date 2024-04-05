



'''
	agenda:
		import rollercoaster.gadgets.clock.UTC.greatness_1 as UTC_greatness_1
		
		UTC_greatness_1_date = UTC_greatness_1.from_UTC_timestamp ()
		UTC_greatness_1_timestamp = UTC_greatness_1.to_UTC_timestamp ()
'''

'''
	{
		"format": "greatness 1",
		
		#
		#	not included -> "0"
		#
		"timezone": "0",
		
		#
		#	-inf to -1, 1 to inf
		#
		"year": 2094,
		
		#
		#	from 1 to 12
		#
		"month": 1,
		
		#
		#	from 1 to either 28,29,30, or 31
		#
		"month day":
		
		#
		#	from 0 to 23
		#
		"hour": 
		
		#
		#	from 0 to 59
		#
		"minute": 
		
		#
		#	from 0 to 59
		#
		"second": 
		
		#
		#	from 0 to 999
		#
		"millisecond":
	}
'''

'''
	https://arrow.readthedocs.io/en/latest/api-guide.html
'''	
import arrow

def from_UNIX_timestamp (UNIX_timestamp):
	return arrow.get (UNIX_timestamp).datetime;
	
	
def to_UNIX_timestamp (greatness_1):
	assert ('year' in greatness_1)
	
	year = greatness_1 ['year']
	
	arrow.Arrow (
		2013, 
		5, 
		5, 
		12, 
		30, 
		45
	)

	return;