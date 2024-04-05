
'''
	ATR: Average True Range
'''

'''
	import rollercoaster.rides.season_1.ATR as ATR_indicator
	
	ATR = ATR_indicator.calc (
		data = [{
            "high": 100,
            "low": 80,
            "close": 99
		}],
		
		spans = 7
	)
'''

'''
	ATR = (1 / spans) * summation (TR, 1, spans)
'''

def summation_TRs (
	places = []
):
	sum = 0
	for place in places:
		sum += place ["TR"]
		
	return sum;
		
def calc_ATR_1 (
	places = [],
	spans = None
):
	summation = summation_TRs (places)
	#print ("summation:", summation)

	return summation / spans
	
def calc (
	places = [],
	
	label = "ATR",
	
	#
	#	The number of places to consider in the
	#	first calculation.
	#
	spans = 7
):
	import rollercoaster.rides.season_1.TR as TR_indicator
	TR_indicator.calc (
		places = places,
		label = "TR"
	)

	assert (len (places) >= spans + 1), [ len (places), spans ]

	'''
		spans = 2
	
			TR = [ 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
			TR [1:] [:spans]
			
			# [ 2, 3 ]
			
		spans = 3
	
			TR = [ 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
			TR [1:] [:spans ]
			
			# [ 2, 3, 4 ]
	'''
	span_1 = places [1:] [:spans];
	assert (len (span_1) >= spans)
	
	
	ATR_1 = calc_ATR_1 (
		places = places [1:] [:spans],
		spans = spans
	)
	
	places [spans] [label] = ATR_1

	'''
		example if:
			spans = 3
			
			            ATR  ATR
			    TR  TR  TR   TR
			[ ][  ][  ][   ][   ]
	'''
	ATR = ATR_1
	
	last_places_index = len (places) - 1;
	s = spans + 1
	while (s <= last_places_index):
		ATR = (
			(ATR * (spans - 1)) + 
			places [s]["TR"]
		) / spans;
		
		places [s] [label] = ATR
	
	
		s += 1;

	'''
	
	'''
	#TR =  

	return;