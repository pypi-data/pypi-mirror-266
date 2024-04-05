

'''
	import rollercoaster.stats.aggregate_break_even as aggregate_break_even
	break_evens = aggregate_break_even.calc ({
		"expirations": []
	})
'''

'''
	priorities: {
		"expirations": [
			{
				"expiration": "2023-10-13",
				"aggregate break even": {
					"calls": {
						"ask":
						"bid":
						"last": 
					},
					"puts": {
						"ask":
						"bid":
						"last": 
					}
				}
			}
		]
	}

'''

from fractions import Fraction as F

prices = [ "ask", "bid", "last" ]

def calc (data):
	expirations = data ["expirations"]
	
	proceeds = {
		"expirations": []
	}
	
	for expiration in expirations:
		calls = expiration ["calls"]
		calls_strikes = expiration ["calls"] ["strikes"]
		
		puts = expiration ["puts"]
		puts_strikes = expiration ["puts"] ["strikes"]
		
		expiration_data = {
			"expiration": expiration ["expiration"],
			"aggregate break even": {
				"calls": {
					"ask": "",
					"bid": "",
					"last": ""
				},
				"puts": {
					"ask": "",
					"bid": "",
					"last": ""
				}
			},
			"aggregate multiplier": {
				"calls": {
					"ask": "",
					"bid": "",
					"last": ""
				},
				"puts": {
					"ask": "",
					"bid": "",
					"last": ""
				}
			}
		}


		contracts = [ "puts", "calls" ]
		for contract in contracts:
			sums = {
				"aggregate": {
					"ask": 0,
					"bid": 0,
					"last": 0
				},
				"confidence": {
					"ask": 0,
					"bid": 0,
					"last": 0
				},
				"multiplier numerator":{
					"ask": 0,
					"bid": 0,
					"last": 0
				}
			}

			for option in expiration [ contract ] ["strikes"]:
				for price in prices:
					try:
						strike = F (option ["strike"])
					
						if (contract == "calls"):
							bet = strike + F (option ["prices"] [ price ])
						else:
							if (strike < F (option ["prices"] [ price ])):
								raise Exception ("?")
						
							bet = strike - F (option ["prices"] [ price ])
						
						confidence = F (option ["prices"] [ price ]) * F (option ["open interest"])
						sum = bet * confidence
						
						sums ["aggregate"] [ price ] += sum
						sums ["confidence"] [ price ] += confidence
						
						if (contract == "calls"):
							sums ["multiplier numerator"] [ price ] += (bet / strike) * confidence
						else:
							sums ["multiplier numerator"] [ price ] += (strike / bet) * confidence
							
							print ("::", float ((strike / bet) * confidence) )
							
					except Exception as E:
						print (E)


			for price in prices:
				try:			
					expiration_data ["aggregate break even"] [ contract ] [ price ] = str (float (
						sums ["aggregate"] [ price ] / sums ["confidence"] [ price ]
					))
					expiration_data ["aggregate multiplier"] [ contract ] [ price ] = str (float (
						sums ["multiplier numerator"] [ price ] / sums ["confidence"] [ price ]
					))
					
				except Exception as E:
					print (E)
				
				
		proceeds ["expirations"].append (expiration_data)

	return proceeds