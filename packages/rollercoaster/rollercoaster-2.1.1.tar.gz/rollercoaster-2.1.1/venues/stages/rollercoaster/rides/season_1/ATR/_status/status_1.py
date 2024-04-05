
'''
	python3 insurance.proc.py rides/season_1/ATR/_status/status_1.py
'''

import rollercoaster.rides.season_1.ATR as ATR_indicator

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
	},
	{
		"high": 40000,
		"low": 39000,
		"close": 39500
	},
	{
		"high": 40000,
		"low": 39000,
		"close": 39500
	},
	{
		"high": 40000,
		"low": 39000,
		"close": 39500
	}]
	
	ATR_indicator.calc (
		#
		#	data 
		#
		places = places,
		label = "ATR 4",
		
		spans = 4
	)
	
	assert ("TR" not in places [0])
	assert ("ATR 4" not in places [3])
	
	assert (places [1] ["TR"] == 820.3819999999978)
	assert (places [2] ["TR"] == 736.9745000000039), places [2]
	assert (places [3] ["TR"] == 920.1709999999948), places [3]

	assert (places [4] ["ATR 4"] == 927.2777499999993), places [4]
	assert (places [5] ["ATR 4"] == 945.4583124999995), places [4]
	assert (places [6] ["ATR 4"] == 959.0937343749996), places [4]
	


	print_json (data = places)
	
	
checks = {
	'check 1': check_1
}