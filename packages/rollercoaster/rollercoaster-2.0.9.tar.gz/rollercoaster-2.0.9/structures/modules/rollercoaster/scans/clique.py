







import click
import rich
import rollercoaster.clouds.TradingView.treasure.technicals_v2 as TV_treasure_tech_v2

from ._clique.ETF import ETF_interests
from ._clique.currency import electronic_money_group
from ._clique.TV import TV_scan

def scans_group ():
	@click.group ("scan")
	def group ():
		pass

	ETF_interests (group)
	electronic_money_group (group)
	TV_scan (group)
		
	return group







#






