




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