



'''
	AAS: Average True Range
'''

'''
	import rollercoaster.rides.season_1.AAS as AAS_indicator
	
	AAS = AAS_indicator.calc (
		data = [{
            "high": 100,
            "low": 80,
            "close": 99
		}],
		
		spans = 7
	)
'''

'''
	AAS = (1 / spans) * summation (TR, 1, spans)
'''

import rollercoaster.rides.season_2.AS as AS_tap

def summation_TRs (
	places = []
):
	sum = 0
	for place in places:
		sum += place ["AS"]
		
	return sum;
		
def calc_AAS_1 (
	places = [],
	spans = None
):
	return summation_TRs (places) / spans
	
def calc (
	places = [],
	
	label = "AAS",
	
	#
	#	The number of places to consider in the
	#	first calculation.
	#
	spans = 7
):
	AS_tap.calc (
		places = places,
		label = "AS"
	)

	'''
	
	'''
	assert (
		len (places) >= spans + 1
	), [ len (places), spans ]


	'''
	
	'''
	span_1 = places [1:] [:spans];
	assert (len (span_1) >= spans)
	
	
	AAS_1 = calc_AAS_1 (
		places = places [1:] [:spans],
		spans = spans
	)
	
	places [spans] [label] = AAS_1


	AAS = AAS_1
	
	last_places_index = len (places) - 1;
	s = spans + 1
	while (s <= last_places_index):
		AAS = (
			(AAS * (spans - 1)) + 
			places [s] ["AS"]
		) / spans;
		
		places [s] [label] = AAS
	
	
		s += 1;

