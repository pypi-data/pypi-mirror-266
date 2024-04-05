
'''
	import rollercoaster.clouds.Tradier.procedures.options.combine as combine_options  
	the_options_chains = combine_options.presently ({
		"symbol": symbol,
		"authorization": authorization
	})
'''


import rollercoaster.clouds.Tradier.v1.markets.options.expirations as options_expirations
import rollercoaster.clouds.Tradier.v1.markets.options.chains as options_chains
import rollercoaster.treasures.options.shapes.shape_1 as shares_shape_1 

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
def parallel (
	the_move,
	parameters
):
	proceeds = []
	
	with ThreadPoolExecutor () as executor:
		the_chains = executor.map (
			the_move, 
			parameters
		)
		executor.shutdown (wait = True)

		for chain in the_chains:
			proceeds.append (chain)
		
	return proceeds

def presently (parameters):
	symbol = parameters ["symbol"]
	authorization = parameters ["authorization"]

	expirations = options_expirations.discover ({
		"symbol": symbol,
		"authorization": authorization
	})
		
	def retrieve_options_chains (expiration):
		the_chain =  options_chains.discover ({
			"symbol": symbol,
			"expiration": expiration,
			"authorization": authorization
		})
				
		return the_chain;

	proceeds = parallel (
		the_move = retrieve_options_chains,
		parameters = expirations
	)

	shares_shape_1.assertions (proceeds)

	return proceeds