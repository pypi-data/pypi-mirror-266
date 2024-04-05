

import rollercoaster.clouds.Tradier.procedures.options.combine as combine_options  
import rollercoaster.climate as climate
import rollercoaster.treasures.options.shapes.shape_1 as shares_shape_1 

def check_1 ():
	Tradier = climate.find ("Tradier")

	options_chains = combine_options.presently ({
		"symbol": "RUN",
		"authorization": Tradier ["authorization"]
	})	
	
	shares_shape_1.assertions (options_chains)
	
	
	#print ("options_chains:", options_chains)

	return;
	
	
checks = {
	'structure of the Tradier options': check_1
}