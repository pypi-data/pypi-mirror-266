




'''
import rollercoaster.climate as climate
climate.change ("ports", {
	"driver": 18871,
	"cluster": 0,
	"http": 0	
})
'''

'''
import rollercoaster.climate as climate
Tradier = climate.find ("Tradier")
'''

import copy

def retrieve_Tradier ():
	import json
	fp = open ("/online/crowns_rollercoaster/mint/tradier.com/online.JSON", "r")
	Tradier_authorization = json.loads (fp.read ()) ["authorization"]
	fp.close ()
	
	return Tradier_authorization
	

climate = {
	"Tradier": {
		"authorization": retrieve_Tradier ()
	}
}

def change (field, plant):
	#global CLIMATE;
	climate [ field ] = plant


def find (field):
	return copy.deepcopy (climate) [ field ]