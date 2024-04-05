
import click
import rich
import rollercoaster.clouds.TradingView.treasure.technicals_v2 as TV_treasure_tech_v2

def TV_scan (group):
	def build_symbols (
		symbols_string, 
		exchange,
		screener = "america"
	):
		symbols_list = [
			symbol.strip () for symbol in symbols_string.split (',')
		]
		
		def parse_symbol (the_symbol, exchange):
			return {
				"symbol": the_symbol,
				"screener": screener,
				"exchange": exchange,
				
				"description": ""
			}
			
		the_symbols = []
		for symbol in symbols_list:
			the_symbols.append (parse_symbol (symbol, exchange))

		return the_symbols
		
		
	'''
		"screener": "crypto",
		"exchange": "COINBASE"
	'''
	@group.command ("TV")
	@click.option (
		'--NYSE', 
		type = click.STRING, 
		required = False,
		help = '--NYSE "BRK.A, BRK.B, LLY, TSM, JPM, V"'
	)
	@click.option (
		'--NASDAQ', 
		type = click.STRING, 
		required = False,
		help = '--NASDAQ "MSFT, AAPL, NVDA, GOOGL, AMZN"'
	)
	@click.option (
		'--AMEX', 
		type = click.STRING, 
		required = False,
		help = '--AMEX "SPY, VOO, IMO, 	SIM"'
	)
	@click.option (
		'--Coinbase', 
		type = click.STRING, 
		required = False,
		help = '--Coinbase "BTCUSD, ETHUSD, SOLUSD, ADAUSD"'
	)
	def TV (nyse, nasdaq, amex, coinbase):	
		nyse_symbols = build_symbols (nyse, "NYSE") if type (nyse) == str else []
		nasdaq_symbols = build_symbols (nasdaq, "NASDAQ") if type (nasdaq) == str else []
		amex_symbols = build_symbols (amex, "AMEX") if type (amex) == str else []
		Coinbase_symbols = build_symbols (coinbase, "COINBASE", "crypto") if type (coinbase) == str else []
		
		print ("lists: https://stockanalysis.com/list/")
		print ("NYSE: https://stockanalysis.com/list/nyse-stocks/")
		print ("NASDAQ: https://stockanalysis.com/list/nasdaq-stocks/")
		print ("AMEX: https://stockanalysis.com/list/nyseamerican-stocks/")
		
		
		combined_symbols = [
			* nyse_symbols,
			* nasdaq_symbols,
			* amex_symbols,
			* Coinbase_symbols
		]
		
		rich.print_json (data = combined_symbols)
		
		symbols_indicators = TV_treasure_tech_v2.scan_symbols (
			capacity = 3,
			symbols = combined_symbols
		)

		TV_treasure_tech_v2.print_symbols_table (symbols_indicators)