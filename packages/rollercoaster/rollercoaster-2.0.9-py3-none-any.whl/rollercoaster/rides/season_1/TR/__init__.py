
'''
	TR: True Range
'''

'''
	import rollercoaster.rides.season_1.TR as TR_indicator
	TR_indicator.calc (
		places = [],
		label = "TR"
	)


	TR_indicator.calc (
		#
		#	data 
		#
		places = [{
            "date string": "2023-11-28 06:00:00",
            "u timestamp": "1701151200",
            "date": 1701151200000,
            "open": 36901.035,
            "high": 38404.3875,
            "low": 36901.035,
            "close": 38056.5515,
            "volume": 2.416483534,
            "trade_count": 114.0,
            "vwap": 37965.0139822184
        },{
            "date string": "2023-11-29 06:00:00",
            "u timestamp": "1701237600",
            "date": 1701237600000,
            "open": 38053.85,
            "high": 38423.07,
            "low": 37602.688,
            "close": 37895.439,
            "volume": 10.206069493,
            "trade_count": 115.0,
            "vwap": 37894.9599072209
        }]
	)
'''

'''
	https://en.wikipedia.org/wiki/Average_true_range
'''

from fractions import Fraction

def calc (
	places = [],
	
	#
	#	label = "TR"
	#
	label = "true range"
):	
	assert (len (places) >= 2)

	last_places_index = len (places) - 1;
	s = 1
	while (s <= last_places_index):
		place_1 = places [s - 1]
		place_2 = places [s]
	
		#
		#	{ span, range }
		#
		span_1 = Fraction (place_2 ["high"]) - Fraction (place_2 ["low"])
		span_2 = abs (Fraction (place_2 ["high"]) - Fraction (place_1 ["close"]))
		span_3 = abs (Fraction (place_2 ["low"]) - Fraction (place_1 ["close"]))
				
		TR = float (max (span_1, span_2, span_3))
		
		places [s] [label] = TR;
		
		s += 1

	'''
	
	'''

	return;


