




'''
	import rich
	from datetime import datetime, timedelta
	import rollercoaster.clouds.TradingView.treasure.technicals_v2 as TV_treasure_tech_v2
	symbols_indicators = TV_treasure_tech_v2.scan_symbols (
		capacity = 2,
		changes = [
			[ 
				datetime.today () - timedelta (days = 1),
				datetime.today ()
			]
		],
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
	
	# rich.print_json (data = symbols_indicators)
	
	TV_treasure_tech_v2.print_symbols_table (symbols_indicators)
'''

'''
	
'''

import rich
from ships.flow.simultaneous import simultaneously
from tradingview_ta import TA_Handler, Interval, Exchange

from .rooms.scan_symbol import scan_symbol
from .rooms.print_symbols_table import print_symbols_table

def retrieve_change ():
	import numpy
	from datetime import datetime, timedelta
	import rollercoaster.clouds.Yahoo.retrieve_change as Yahoo_retrieve_change
	change = Yahoo_retrieve_change.perfectly (
		symbol = "DFEN",
		date_1 = datetime.today () - timedelta (days = 10),
		date_2 = datetime.today ()
	)


def scan_symbols (
	symbols = [],
	changes = [],
	capacity = 2,
):
	symbols_indicators = simultaneously (
		items = symbols,
		capacity = capacity,
		move = scan_symbol
	)
	
	sorted_symbols_indicators = sorted (
		symbols_indicators, 
		key = lambda x: x ["technicals sum"],
		reverse = True
	)
	
	return sorted_symbols_indicators


