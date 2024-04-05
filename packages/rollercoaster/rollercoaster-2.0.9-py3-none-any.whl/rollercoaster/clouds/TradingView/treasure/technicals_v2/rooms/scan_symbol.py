


import rich
from ships.flow.simultaneous import simultaneously
from tradingview_ta import TA_Handler, Interval, Exchange

def scan_symbol (item):
	symbol = item ["symbol"]
	screener = item ["screener"]
	exchange = item ["exchange"]
	
	
	
	if ("description" in item):
		description = item ["description"]
	else:
		description = ""
	
	print ("scanning:", symbol)
	
	def move (interval):	
		try:
			treasure = TA_Handler (
				symbol = symbol,
				screener = screener,
				exchange = exchange,
				interval = interval
			)
			
			summary = treasure.get_analysis().summary
			
			aggregate = str (summary ["BUY"] - summary ["SELL"])
			if (aggregate [0] != "-"):
				aggregate = "+" + aggregate
			
			summary = {
				"interval": interval,
				"technicals": aggregate
			}
			
			return summary
			
		except Exception:
			pass;
			
		return {
			"interval": interval,
			"technicals": "?"
		}


	technicals = simultaneously (
		items =  [
			Interval.INTERVAL_1_MINUTE,
			Interval.INTERVAL_5_MINUTES,
			Interval.INTERVAL_15_MINUTES,
			Interval.INTERVAL_1_HOUR,
			Interval.INTERVAL_2_HOURS,
			Interval.INTERVAL_4_HOURS,
			Interval.INTERVAL_1_DAY,
			Interval.INTERVAL_1_DAY,
			Interval.INTERVAL_1_WEEK,
			Interval.INTERVAL_1_MONTH
		],
		capacity = 20,
		move = move
	)
	
	technicals_parsed = {}
	for technical in technicals:
		technicals_parsed [ technical ["interval"] ] = technical ["technicals"]
	
	
	#for technical in technicals:
	techincals_sum = 0
	for technical in technicals_parsed:
		#print (technicals_parsed [ technical ])
	
		try:
			techincals_sum += int (technicals_parsed [ technical ])
		except Exception:
			pass;
		
	
	return {
		"symbol": symbol,
		"screener": screener,
		"exchange": exchange,
		"description": description,
		
		"technicals": technicals_parsed,
		"technicals sum": techincals_sum
	};
	