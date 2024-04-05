
'''
	python3 insurance.proc.py rides/season_2/AS/_status/status_1.py
'''

import rollercoaster.rides.season_2.AS as AS_tap

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
	
	AS_tap.calc (
		#
		#	data 
		#
		places = places,
		label = "AS"
	)
	
	print_json (data = places)
	
	
	assert (places [1] ["AS"] == 820.3819999999978)
	
	
	
checks = {
	'check 1': check_1
}