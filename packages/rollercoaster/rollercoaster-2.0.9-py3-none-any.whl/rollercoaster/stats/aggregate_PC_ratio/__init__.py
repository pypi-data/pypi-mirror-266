
'''
	Tradier_API_authorization = ""
		
	import rollercoaster.stats.aggregate_PC_ratio as aggregate_PC_ratio
	import rollercoaster.clouds.Tradier.procedures.options.combine as combine_options  
	PC_ratios = aggregate_PC_ratio.calc ({
		"expirations": combine_options.presently ({
			"symbol": "OTLY",
			"authorization": Tradier_API_authorization
		})
	})

	import rich
	rich.print_json (data = {
		"PC ratios": PC_ratios
	})
'''

'''
	output:
	
		{
			"expirations": [{
				"expiration": "2023-10-27",
				"sums": {
					"puts": {
						"ask":
						"bid":
						"last"
					},
					"calls": {
						"ask":
						"bid":
						"last"
					}
				},
				"PC ratios": {
					"ask":
					"bid":
					"last"
				}
			}],
			"sums": {
				"puts": {
					"ask":
					"bid":
					"last"
				},
				"calls": {
					"ask":
					"bid":
					"last"
				}
			},
			"PC ratios": {
				"ask":
				"bid":
				"last"
			}
		}
'''

from rollercoaster.gadgets.ratio import calculate_ratio

import pydash
def return_number (OBJECT, PATH, DEFAULT):
	FOUND = pydash.get (
		OBJECT,
		PATH,
		DEFAULT
	)
	
	TYPE = type (FOUND)
	if (TYPE == int or TYPE == float):
		return FOUND
		
	if (FOUND == None):
		return DEFAULT;

	print ("FOUND WAS NOT ACCOUNTED FOR:", FOUND)
	raise Exception (f"FOUND WAS NOT ACCOUNTED FOR: { FOUND }")
		
	return DEFAULT

def retrieve_multiplicand (strike):
	return strike ["contract size"] * strike ["open interest"]
 
	try:
		pass;
	
	except Exception as E:
		pass;
		

def EQUALITY_CHECK (PARAM_1, PARAM_2):
	try:
		assert (PARAM_1 == PARAM_2)
	except Exception as E:
		import traceback
		
		print ("PARAM 1", PARAM_1)
		print ("PARAM 2", PARAM_2)	
		
		print (traceback.print_exception (E))

		raise Exception (E)

	return
	

def calc (chain):
	expirations = chain ["expirations"]
	
	evaluation = {
		"expirations": [],
		"sums": {
			"puts": {
				"ask": 0,
				"bid": 0,
				"last": 0
			},
			"calls": {
				"ask": 0,
				"bid": 0,
				"last": 0
			}
		},
		"PC ratios": {
			"ask": 0,
			"bid": 0,
			"last": 0
		}
	}
	
	
	for expiration in expirations:
		calls_strikes = expiration ["calls"]["strikes"]
		puts_strikes = expiration ["puts"]["strikes"]
		
		expiration_note = {
			"expiration": expiration ["expiration"],
			"sums": {
				"puts": {
					"ask": 0,
					"bid": 0,
					"last": 0
				},
				"calls": {
					"ask": 0,
					"bid": 0,
					"last": 0
				}
			},
			"PC ratios": {
				"ask": 0,
				"bid": 0,
				"last": 0
			}
		}
		
		EQUALITY_CHECK (len (calls_strikes), len (puts_strikes))
		
		direction = "calls"
		for strike in calls_strikes:		
			expiration_note ["sums"][ direction ]["ask"] += (
				return_number (strike, [ "prices", "ask" ], 0) * 
				retrieve_multiplicand (strike)
			)
			expiration_note ["sums"][ direction ]["bid"] += (
				return_number (strike, [ "prices", "bid" ], 0) * 
				retrieve_multiplicand (strike)
			)
			expiration_note ["sums"][ direction ]["last"] += (
				return_number (strike, [ "prices", "last" ], 0) * 
				retrieve_multiplicand (strike)
			)
		
		direction = "puts"
		for strike in puts_strikes:		
			expiration_note ["sums"][ direction ]["ask"] += (
				return_number (strike, [ "prices", "ask" ], 0) * 
				retrieve_multiplicand (strike)
			)
			expiration_note ["sums"][ direction ]["bid"] += (
				return_number (strike, [ "prices", "bid" ], 0) * 
				retrieve_multiplicand (strike)
			)
			expiration_note ["sums"][ direction ]["last"] += (
				return_number (strike, [ "prices", "last" ], 0) * 
				retrieve_multiplicand (strike)
			)
		
		expiration_note ["PC ratios"]["ask"] = calculate_ratio (
			expiration_note ["sums"][ "puts" ]["ask"],
			expiration_note ["sums"][ "calls" ]["ask"]
		)
		expiration_note ["PC ratios"]["bid"] = calculate_ratio (
			expiration_note ["sums"][ "puts" ]["bid"],
			expiration_note ["sums"][ "calls" ]["bid"]
		)
		expiration_note ["PC ratios"]["last"] = calculate_ratio (
			expiration_note ["sums"][ "puts" ]["last"],
			expiration_note ["sums"][ "calls" ]["last"]
		)
		
		evaluation ["sums"][ "calls" ]["ask"] += return_number (expiration_note, [ "sums", "calls", "ask" ], 0)
		evaluation ["sums"][ "calls" ]["bid"] += return_number (expiration_note, [ "sums", "calls", "bid" ], 0)
		evaluation ["sums"][ "calls" ]["last"] += return_number (expiration_note, [ "sums", "calls", "last" ], 0)
		
		evaluation ["sums"][ "puts" ]["ask"] += return_number (expiration_note, [ "sums", "puts", "ask" ], 0)
		evaluation ["sums"][ "puts" ]["bid"] += return_number (expiration_note, [ "sums", "puts", "bid" ], 0)
		evaluation ["sums"][ "puts" ]["last"] += return_number (expiration_note, [ "sums", "puts", "last" ], 0)
		
		evaluation ["expirations"].append (expiration_note)
		
	evaluation ["PC ratios"]["ask"] = calculate_ratio (
		evaluation ["sums"][ "puts" ]["ask"],
		evaluation ["sums"][ "calls" ]["ask"]
	)
	
	evaluation ["PC ratios"]["bid"] = calculate_ratio (
		evaluation ["sums"][ "puts" ]["bid"],
		evaluation ["sums"][ "calls" ]["bid"]
	)
	
	evaluation ["PC ratios"]["last"] = calculate_ratio (
		evaluation ["sums"][ "puts" ]["last"],
		evaluation ["sums"][ "calls" ]["last"]
	)

	return evaluation