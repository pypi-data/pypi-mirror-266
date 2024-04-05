
'''
	venturing smooth average
'''

'''
	import rollercoaster.rides.season_3.VSA as VSA_tap
	VSA_tap.calc (places)
'''

def calc (
	places, 
	smoothing = 0.2
):
	places [0] ["VSA"] = places [0] ["close"]

	places_span = 10

	S = 1;
	last_index = len (places) - 1;
	while (S < last_index):
		places [S] ["VSA"] = (
			(smoothing * places [S] ["close"]) +
			(1 - smoothing) *
			places [S - 1] ["VSA"]
		)

		'''
		v1 = (2 / (places_span + 1))
		places [S] ["VSA"] = (
			(places [S] ["close"] * v1) +
			(places [S - 1] ["VSA"] * (1 - v1))
		)
		'''
		
		

		S += 1

