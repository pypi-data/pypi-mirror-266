




from .group import clique as clique_group

from rollercoaster.stats.clique import stats_group
from rollercoaster.scans.clique import scans_group

def clique ():
	import click
	@click.group ()
	def group ():
		pass

	import click
	@click.command ("help")
	@click.option ('--port', default = "20000", required = False)
	def open_sphene (port):	
		import pathlib
		from os.path import dirname, join, normpath
		this_folder_path = pathlib.Path (__file__).parent.resolve ()
		this_module_path = normpath (join (this_folder_path, "../.."))

		import somatic
		somatic.start ({
			"extension": ".s.HTML",
			"directory": str (this_module_path),
			"relative path": str (this_module_path),
			
			"port": int (port)
		})

		import time
		while True:
			time.sleep (1000)


	import click
	import rich
	import rollercoaster.clouds.TradingView.treasure.technicals as TV_treasure_tech
	@click.command ("ETFs")
	def example_command ():	
		def symbol (the_symbol, description = ""):
			return {
				"symbol": the_symbol,
				"screener": "america",
				"exchange": "AMEX",
				
				"description": description
			}
	
		#
		#	rollercoaster/structures/ride/season_1/TV_technicals_shares/ETF/rise.proc.py
		#
	
		
		symbols_indicators = TV_treasure_tech.scan_symbols (
			symbols = [
				symbol ("Cruise", "Travel"),
				#symbol ("DFEN", "peace"),
				symbol ("JETS", "airlines"),
				symbol ("KIE", "insurance"),
				symbol ("MSOS", "cannabis"),
				symbol ("PJP", "biotech pharmaceuticals"),
				symbol ("LABU", "biotech x3"),
				symbol ("VOO", "")				
			]
		)

		rich.print_json (data = symbols_indicators)

		TV_treasure_tech.print_symbols_table (symbols_indicators)

	group.add_command (example_command)
	group.add_command (open_sphene)

	group.add_command (clique_group ())
	group.add_command (stats_group ())	
	group.add_command (scans_group ())	
	
	
	group ()




#
