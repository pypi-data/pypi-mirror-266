



'''
	PSA: Average True Range
'''

'''
	import rollercoaster.rides.season_3.physical_span_average as PSA_rides
	PSA = PSA_rides.calc (
		places = ,
		spans = 7
	)
'''

'''
	PSA = (1 / spans) * summation (TR, 1, spans)
'''

import rollercoaster.rides.season_3.physical_span as PS_rides

def summation_PSs (
	places = []
):
	sum = 0
	for place in places:
		sum += place ["PS"]
		
	return sum;

def calc_PSA_1 (
	places = [],
	spans = None
):
	return summation_PSs (places) / spans
	
def calc (
	places = [],
	
	label = "PSA",
	
	#
	#	The number of places to consider in the
	#	first calculation.
	#
	spans = 7
):
	assert (len (places) >= spans + 1), [ len (places), spans ]
	
	PS_rides.calc (
		places = places,
		label = "PS"
	)


	'''
	
	'''
	span_1 = places [1:] [:spans];
	assert (len (span_1) >= spans)
	
	#PSA_1 = summation_PSs (places) / spans
	
	PSA_1 = calc_PSA_1 (
		places = places [1:] [:spans],
		spans = spans
	)
	
	
	places [spans] [label] = PSA_1

	PSA = PSA_1
	

	
	last_places_index = len (places) - 1;
	s = spans + 1
	while (s <= last_places_index):
		PSA = (
			(PSA * (spans - 1)) + 
			places [s] ["PS"]
		) / spans;
		
		places [s] [label] = PSA
	
		s += 1;

