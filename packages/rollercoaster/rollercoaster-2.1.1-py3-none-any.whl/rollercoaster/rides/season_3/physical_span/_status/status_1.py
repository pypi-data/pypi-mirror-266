
'''
	python3 insurance.proc.py rides/season_2/PS/_status/status_1.py
'''

import rollercoaster.rides.season_3.physical_span as PS_tap

from rich import print_json

def check_1 ():	
	places = [{
		"high": 38404.3875,
		"low": 36901.035,
		"close": 38056.5515
	},{
		"high": 38423.07,
		"low": 37602.688,
		"close": 37895.439
	}]
	
	PS_tap.calc (
		#
		#	data 
		#
		places = places,
		label = "PS"
	)
	
	print_json (data = places)
	
	
	assert (places [1] ["PS"] == 820.3819999999978)
	
	
	
checks = {
	'check 1': check_1
}