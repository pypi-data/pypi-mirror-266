
'''
	python3 insurance.proc.py rides/season_2/AS/_status/status_2.py
'''

import rollercoaster.rides.season_2.AS as AS_tap

from rich import print_json

def check_1 ():	
	places = [{
		"high": 38404.3875,
		"low": 36901.035,
		"close": 38056.5515
	},
	{
		"high": 38423.07,
		"low": 37602.688,
		"close": 37895.439
	},
	{
		"high": 38251.5645,
		"low": 37514.59,
		"close": 38153.885
	},
	{
		"high": 39002.916,
		"low": 38082.745,
		"close": 38768.4165
	}]
	
	AS_tap.calc (
		#
		#	data 
		#
		places = places
	)
	
	print_json (data = places)
	
	
	assert (places [1] ["actual span"] == 820.3819999999978)
	assert (places [2] ["actual span"] == 736.9745000000039), places [2]
	assert (places [3] ["actual span"] == 920.1709999999948), places [3]
	
	
checks = {
	'check 1': check_1
}