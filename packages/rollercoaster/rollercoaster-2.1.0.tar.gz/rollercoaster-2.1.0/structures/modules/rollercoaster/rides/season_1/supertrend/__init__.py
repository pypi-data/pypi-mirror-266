
'''
	import rollercoaster.rides.season_1.supertrend as supertrend_indicator
	supertrend_indicator.calc (
		places = [],
		spans = 4
	)
'''

import rollercoaster.rides.season_1.ATR as ATR_indicator

def calc (
	places = [],
	spans = None,
	multiplier = 1.4
):
	ATR_indicator.calc (
		places = places,
		label = "ATR",
		
		spans = spans
	)
	
	for i in range (spans, len (places)):
		if ("ATR" not in places [i]):
			continue;
			
		place_1 = places [i - 1]
		place_2 = places [i]
	
		upper_band = place_1 ['close'] + multiplier * place_2 ['ATR']
		lower_band = place_1 ['close'] - multiplier * place_2 ['ATR']
		end = place_1 ['close']

		if end > upper_band:
			place_2 ['supertrend'] = lower_band
			place_2 ['position'] = 1  # Buy Signal
			
			print ("Buy")
			
		elif end < lower_band:
			place_2 ['supertrend'] = upper_band
			place_2 ['position'] = -1  # Sell Signal

			print ("Sell")

		else:
			print ("in between bands")
		
			try:
				place_2 ['supertrend'] = place_1 ['supertrend']
				place_2 ['position'] = 0
			except Exception:
				#print ('exception:', Exception)
				pass;
			
		