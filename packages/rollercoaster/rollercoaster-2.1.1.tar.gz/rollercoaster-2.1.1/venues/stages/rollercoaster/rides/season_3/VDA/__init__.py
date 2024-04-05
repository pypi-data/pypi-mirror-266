
'''
	venturing distance average
'''

'''
	import rollercoaster.rides.season_3.VDA as VDA_tap
	VDA_tap.calc (places)
'''

def calc (
	places, 
	smoothing = 0.2
):
	places [0] ["VDA"] = places [0] ["close"]
	places_span = 10

	S = 1;
	last_index = len (places) - 1;
	while (S < last_index):
		v1 = (2 / (places_span + 1))
		places [S] ["VDA"] = (
			(places [S] ["close"] * v1) +
			(places [S - 1] ["VDA"] * (1 - v1))
		)

		S += 1

