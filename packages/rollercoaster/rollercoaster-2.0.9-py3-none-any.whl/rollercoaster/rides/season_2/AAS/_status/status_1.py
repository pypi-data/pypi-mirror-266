
'''
	python3 insurance.proc.py rides/season_2/AAS/_status/status_1.py
'''

import rollercoaster.rides.season_2.AAS as AAS_tap

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
	
	AAS_tap.calc (
		#
		#	data 
		#
		places = places,
		label = "AAS 4",
		
		spans = 4
	)
	
	assert ("AS" not in places [0])
	assert ("AAS 4" not in places [3])
	
	assert (places [1] ["AS"] == 820.3819999999978)
	assert (places [2] ["AS"] == 736.9745000000039), places [2]
	assert (places [3] ["AS"] == 920.1709999999948), places [3]

	assert (places [4] ["AAS 4"] == 927.2777499999993), places [4]
	assert (places [5] ["AAS 4"] == 945.4583124999995), places [4]
	assert (places [6] ["AAS 4"] == 959.0937343749996), places [4]
	


	print_json (data = places)
	
	
checks = {
	'check 1': check_1
}