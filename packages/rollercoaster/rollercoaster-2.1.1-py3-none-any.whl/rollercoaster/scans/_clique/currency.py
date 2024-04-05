

import click
import rich
import rollercoaster.clouds.TradingView.treasure.technicals_v2 as TV_treasure_tech_v2

#
#	# currency
#
def electronic_money_group (group):
	the_options = [ '' ]

	def validate_option(ctx, param, value):	
		if value not in the_options:
			raise click.BadParameter (f'''
				
	The options are: 
		{ ", ".join (the_options) }
	
			''')
		
		return value

	import click
	@group.command ("currency-interests")
	def interests ():
		print (f'''
				
	The options are: 
		{ ", ".join (the_options) }
	
			''')

	import click
	@group.command ("currency")
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
	
		def symbol (the_symbol):
			return {
				"symbol": the_symbol,
				"screener": "crypto",
				"exchange": "COINBASE"
			}
			
		front = [
			symbol ("BOBAUSD"),
			symbol ("ACHUSD"),
			symbol ("MSOLUSD"),
			symbol ("MUSEUSD")			
		]	
		
		the_symbols = front;
		#if (interest == 'airlines'):
		#	the_symbols = airlines

		rich.print_json (data = front)
		
		symbols_indicators = TV_treasure_tech_v2.scan_symbols (
			capacity = 3,
			symbols = the_symbols
		)

		#rich.print_json (data = symbols_indicators)
		TV_treasure_tech_v2.print_symbols_table (symbols_indicators)
