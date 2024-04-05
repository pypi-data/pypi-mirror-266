

import click
import rich
import rollercoaster.clouds.TradingView.treasure.technicals_v2 as TV_treasure_tech_v2

def ETF_interests (group):
	the_options = [ '', 'airlines', 'biotech', 'currency', 'real_estate' ]

	def validate_option (ctx, param, value):	
		if value not in the_options:
			raise click.BadParameter (f'''
				
	The options are: 
		{ ", ".join (the_options) }
	
			''')
		
		return value

	import click
	@group.command ("ETF-interests")
	def interests ():
		print (f'''
				
	The options are: 
		{ ", ".join (the_options) }
	
			''')

	import click
	@group.command ("ETF")
	@click.option (
		'--interest', 
		type = click.STRING, 
		callback = validate_option,
		default = '',
		required = False,
		help = 'The sector, command "scan ETF-interests" enumerates the interests'
	)	
	def search (interest):
		print ("interest:", interest)
	
		def symbol (the_symbol, description = "", exchange = "AMEX"):
			return {
				"symbol": the_symbol,
				"screener": "america",
				"exchange": exchange,
				
				"description": description
			}
			
		front = [
			symbol ("BITQ", "currency"),
			symbol ("Cruise", "Travel"),
			#symbol ("DFEN", "peace"),
			symbol ("FDN", "internet"),
			symbol ("JETS", "airlines"),
			symbol ("KIE", "insurance"),
			symbol ("MSOS", "cannabis"),
			symbol ("PSI", "semiconductors"),
			symbol ("PJP", "biotech pharmaceuticals"),
			symbol ("LABU", "biotech x3"),
			symbol ("VNQ", "real estate"),
			symbol ("VOO", "")				
		]	
		
		airlines = [{
			"symbol": "DAL",
			"screener": "america",
			"exchange": "NYSE",
			
			"description": "Delta"
		},{
			"symbol": "RYAAY",
			"screener": "america",
			"exchange": "NYSE",
			
			"description": "Ryanair"
		},{
			"symbol": "LUV",
			"screener": "america",
			"exchange": "NYSE",
			
			"description": "Southwest"
		},{
			"symbol": "UAL",
			"screener": "america",
			"exchange": "NASDAQ",
			
			"description": "United"
		},{
			"symbol": "AAL",
			"screener": "america",
			"exchange": "NASDAQ",
			
			"description": "American"
		},{
			"symbol": "ALK",
			"screener": "america",
			"exchange": "NYSE",
			
			"description": "Alaska"
		},{
			"symbol": "CPA",
			"screener": "america",
			"exchange": "NYSE",
			
			"description": "Copa"
		},{
			"symbol": "JBLU",
			"screener": "america",
			"exchange": "NASDAQ",
			
			"description": "Jet Blue"
		},{
			"symbol": "ALGT",
			"screener": "america",
			"exchange": "NASDAQ",
			
			"description": "Allegiant"
		}]
		
		biotech = [
			symbol ("CANC", "oncology", "NASDAQ"),
			symbol ("CNCR", "oncology, therapeutics", "NASDAQ"),
			symbol ("GNOM", "genetics", "NASDAQ"),
			symbol ("IDNA", "genomics, immunotherapy", "NASDAQ"),
			symbol ("WDNA", "biorevolution"),
		]
		
		currency = [
			symbol ("COIN", "coinbase", "NASDAQ"),
			symbol ("MSTR", "MicroStrategy", "NASDAQ"),
		]
		
		#
		#	banjo money
		#	FX
		#
		country_money = []
		
		#
		#	https://etfdb.com/etfdb-category/real-estate/
		#
		real_estate = [
			symbol ("VNQ", "Vanguard Real Estate ETF"),
			symbol ("SCHH", "Schwab US REIT ETF"),
			symbol ("XLRE", "Real Estate Select Sector SPDR Fund"),
			symbol ("IYR", "iShares U.S. Real Estate ETF"),
			symbol ("REM", "iShares Mortgage Real Estate ETF"),
			symbol ("RWR", "SPDR Dow Jones REIT ETF")
		]
		
		semiconductors = []
		
		if (interest == ''):
			the_symbols = front;
		elif (interest == 'airlines'):
			the_symbols = airlines
		elif (interest == 'biotech'):
			the_symbols = biotech
		elif (interest == 'currency'):
			the_symbols = currency
		elif (interest == 'real_estate'):
			print (f"""
			
				mortage interest rate in the USA:
					https://www.tradingview.com/chart/?symbol=ECONOMICS%3AUSMR
			
			""")
			the_symbols = real_estate
		else:
			print (f'Interest "{ interest }" was not found.')
			return;
		
		symbols_indicators = TV_treasure_tech_v2.scan_symbols (
			capacity = 3,
			symbols = the_symbols
		)

		#rich.print_json (data = symbols_indicators)
		TV_treasure_tech_v2.print_symbols_table (symbols_indicators)
