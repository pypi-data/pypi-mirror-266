

'''
	itinerary:
		data points: 
			1 YR change
			
		current market cap
'''

'''
	import rollercoaster.clouds.TradingView.treasure.technicals as TV_treasure_tech
	symbols_indicators = TV_treasure_tech.scan_symbols (
		symbols = [{
			"symbol": "TSLA",
			"screener": "america",
			"exchange": "NASDAQ",
			"description": "Tesla"
		},{
			"symbol": "OTLY",
			"screener": "america",
			"exchange": "NASDAQ"
		}]
	)
	
	rich.print_json (data = symbols_indicators)
	TV_treasure_tech.print_symbols_table (symbols_indicators)
'''

'''
	
'''

import rich
from ships.flow.simultaneous import simultaneously
from tradingview_ta import TA_Handler, Interval, Exchange


def retrieve_change ():
	import numpy
	from datetime import datetime, timedelta
	import rollercoaster.clouds.Yahoo.retrieve_change as Yahoo_retrieve_change
	change = Yahoo_retrieve_change.perfectly (
		symbol = "DFEN",
		date_1 = datetime.today () - timedelta (days = 10),
		date_2 = datetime.today ()
	)

'''
	The scan of one symbol
'''
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
	
	
	



def scan_symbols (
	symbols = [],
	capacity = 2,
):
	symbols_indicators = simultaneously (
		items = symbols,
		capacity = capacity,
		move = scan_symbol
	)
	
	sorted_symbols_indicators = sorted (
		symbols_indicators, 
		key=lambda x: x["technicals sum"],
		reverse = True )
	
	return sorted_symbols_indicators




'''
				company
	interval			1m			5m		15m
				TSLA	16,10,0		14,9,3	11,10,5
				TSLA	16,10,0		14,9,3	11,10,5
'''
from tabulate import tabulate

def print_symbols_table (symbols_indicators):
	headers = ["", "description", "1m", "5m", "15m", "1h", "2h", "4h", "1d", "1W", "1M", "sum" ]
	
	rows = []
	for symbols_indicator in symbols_indicators:
		symbol = symbols_indicator ["symbol"]
		technicals = symbols_indicator ["technicals"]
		
		rows.append ([ 
			symbol, 
			symbols_indicator ["description"],
			technicals ["1m"], 
			technicals ["5m"],
			technicals ["15m"], 
			technicals ["1h"], 
			technicals ["2h"], 
			technicals ["4h"], 
			technicals ["1d"], 
			technicals ["1W"], 
			technicals ["1M"],
			symbols_indicator ["technicals sum"]
		])

	print (tabulate(rows, headers=headers, tablefmt="grid"))