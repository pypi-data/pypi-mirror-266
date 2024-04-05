


'''
	import rollercoaster.rides.season_1.pecdency as pecdency_indicator
	pecdency_indicator.calc (
		places = [],
		
		spans = 4,
		multiplier = 1.4
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
		close = place_1 ['close']

		place_2 ['pecdency UB'] = upper_band
		place_2 ['pecdency LB'] = lower_band

		print (
			place_1 ['UTC date string'],
			upper_band - close,
			close - lower_band,
			lower_band, close, upper_band
		)

		if close > upper_band:
			place_2 ['pecdency'] = lower_band
			
			# Incline Signal
			place_2 ['direction'] = 1
			
			print ("Incline")
			
		elif close < lower_band:
			place_2 ['pecdency'] = upper_band
			
			# Decline Signal
			place_2 ['direction'] = -1

			print ("Decline")

		else:
			#print ("in between bands")
		
			try:
				place_2 ['pecdency'] = place_1 ['pecdency']
				place_2 ['direction'] = 0
			except Exception:
				#print ('exception:', Exception)
				pass;
			
		