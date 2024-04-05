


'''
	import rollercoaster.rides.season_3.super_hero_trend.win_rates.shares_trading as SHT_WR_shares_trading
	SHT_WR_shares_trading.calc (data)
'''

from fractions import Fraction
def calc (DF):
	win_rate = 1

	previous_amount = None;
	previous_signal = None;
	
	last_sell_signal = None
	last_buy_signal = None
	
	bought_at = None
	sold_at = None
	
	'''
		find BUY signal to SELL signal multiplier.
	'''	
	for index, row in DF.iterrows ():
		signal = row ['ST_BUY_SELL']
		
		#print (signal, previous_signal)
		
		if (signal == "SELL"):
			last_sell_signal = row ["close"]
		elif (signal == "BUY"):
			last_buy_signal = row ["close"]
		
		if (signal == "BUY" and previous_signal == "SELL"):
			#print ("BUY!", last_sell_signal)
			
			bought_at = Fraction (row ["close"])
			
			'''
			if (type (sold_at) == Fraction):
				multiplier = Fraction (row ["close"]) / Fraction (sold_at)	
				win_rate = win_rate * multiplier

				print ({
					"win rate": float (win_rate),
					"multiplier": float (multiplier),
					"span": [ float (bought_at), float (sold_at) ]
				})
			'''
			
		if (signal == "SELL" and previous_signal == "BUY"):
			#print ("SELL!", last_buy_signal, type (bought_at))
			
			sold_at = Fraction (row ["close"])
			
			if (type (bought_at) == Fraction):
				multiplier = Fraction (row ["close"]) / Fraction (bought_at)	
				win_rate = win_rate * multiplier

				print ({
					"win rate": float (win_rate),
					"multiplier": float (multiplier),
					"span": [ float (bought_at), float (sold_at) ]
				})
			
			
		previous_signal = signal;
		
	
	actual_change = float (
		Fraction (DF ["close"].iloc [-1]) / Fraction (DF ["close"].iloc [0])
	)	
		
	print ("win_rate:", float (win_rate))
	print ("actual change:", actual_change)
	
	
	return;