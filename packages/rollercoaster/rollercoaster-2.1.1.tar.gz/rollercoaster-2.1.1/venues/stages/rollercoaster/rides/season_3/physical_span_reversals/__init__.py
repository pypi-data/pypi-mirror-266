
'''
	import rollercoaster.rides.season_3.physical_span_reversals as PSR
	PSR.calc ()
'''

'''
	https://tradingstrategy.ai/docs/_modules/pandas_ta/overlap/supertrend.html
'''

from fractions import Fraction

def calc (
	places, 
	spans = 14, 
	multiplier = 1.0
):
	'''
		This calculates spans between high, low, and close prices.
	'''
	import rollercoaster.rides.season_3.physical_span as PS_rides
	PS_rides.calc (
		places = places,
		label = "PS"
	)
	
	import rich
	rich.print_json (data = places)
	
	'''
	
	'''
	import rollercoaster.rides.season_3.physical_span_average as PSA_rides
	PSA = PSA_rides.calc (
		places = places,
		spans = spans
	)

	'''
		source = 
			((place_2 ["high"] + place_2 ["low"]) / 2)
			
		source = 
			open
			
		source = 
			close
			
		upper_band = candle['high'] + multiplier * atr
        lower_band = candle['low'] - multiplier * atr
	'''
	
	def upper_band_source (prices):
		return (prices ["high"] + prices ["low"]) / 2
		
	def lower_band_source (prices):
		return (prices ["high"] + prices ["low"]) / 2
	
	last_places_index = len (places) - 1;
	s = 1
	while (s <= last_places_index):
		place_1 = places [s - 1]
		place_2 = places [s]
		
		try:
			places [s] ["PSR UB"] = (
				upper_band_source (place_2) +
				(multiplier * place_2 ["PSA"])
			)
			places [s] ["PSR LB"] = (
				lower_band_source (place_2) -
				(multiplier * place_2 ["PSA"])
			)
		except Exception:
			pass;
			
		s += 1
		

	
	last_places_index = len (places) - 1;
	S = 1
	while (S <= last_places_index):
		place_1 = places [S - 1]
		place_0 = places [S]
		
		print ("PSR calc?")
		
		'''
			trend := 
				trend == -1 and close > lower_band_1 ? 
					1 : 
					trend == 1 and close < upper_band_1 ? -1 : trend
					
			if (
				place_1 ["PSR direction"] == -1 and 
				place_0 ['close'] > place_0 ["PSR LB"]
			):
				place_0 ["PSR direction"] = 1
				
			elif (
				place_1 ["PSR direction"] == 1 and 
				place_0 ['close'] < place_0 ["PSR UB"]
			):
				place_0 ["PSR direction"] = -1
				
			else:
				place_0 ["PSR direction"] = place_0 ["PSR direction"]
				
				
			if (place_0 ["PSR direction"] == -1):
				place_0 ["PSR"] = place_0 ["PSR LB"]
			else:
				place_0 ["PSR"] = place_0 ["PSR UB"]
		'''
		try:
			if ("PSR direction" not in place_1):
				place_0 ["PSR direction"] = 1;
		
			elif (
				place_1 ["PSR direction"] == -1 and 
				place_0 ['close'] > place_0 ["PSR LB"]
			):
				place_0 ["PSR direction"] = 1
				
			elif (
				place_1 ["PSR direction"] == 1 and 
				place_0 ['close'] < place_0 ["PSR UB"]
			):
				place_0 ["PSR direction"] = -1
			
			else:
				place_0 ["PSR direction"] == place_1 ["PSR direction"] 
			
				
			if (place_0 ["PSR direction"] == -1):
				place_0 ["PSR"] = place_0 ["PSR LB"]
			else:
				place_0 ["PSR"] = place_0 ["PSR UB"]
				
				
				
			'''
			place_2 ["PSR"] = 0
		
			if place_2 ['close'] > place_2 ["PSR UB"]:
				place_2 ["PSR"] = 1
			elif place_2 ['close'] < place_2 ["PSR LB"]:
				place_2 ["PSR"] = -1
			'''

		except Exception as E:
			print ("PSR Exception:", E)
		
			pass;
			
		S += 1

	'''
	for i, candle in enumerate (places):
		print ("i:", i)

		if (i == 0):
			continue;
	
		high = candle ['high']
		low = candle ['low']
		close = candle ['close']
		
		PS = candle ["PS"]
		PSA = candle ["PSA"]
	
		if i == 0:
			PSA = PS
			upper_band = high + multiplier * PSA
			lower_band = low - multiplier * PSA
		else:
			PSA = ((spans - 1) * PSA + PS) / spans
			upper_band = high + multiplier * PSA
			lower_band = low - multiplier * PSA

		PSA_1 = ((high + low) / 2) + (multiplier * PSA)


		if i == 0 or places [i - 1] ['close'] <= PSA:
			PSA = upper_band
		else:
			PSA = lower_band

	'''

	return places