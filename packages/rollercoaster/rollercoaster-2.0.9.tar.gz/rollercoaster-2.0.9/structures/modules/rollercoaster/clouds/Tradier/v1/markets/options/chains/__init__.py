

'''
	import rollercoaster.clouds.Tradier.v1.markets.options.chains as options_chains
	options_chains.discover ({
		"symbol": "",
		"expiration": "",
		"authorization": ""
	})
'''


import rollercoaster.clouds.Tradier.v1.markets.options.chains.parse_1 as parse_1
import requests
import json
import traceback

import rich

def discover (params):
	symbol = params ["symbol"]
	expiration = params ["expiration"]
	authorization = params ["authorization"]
	
	parse_format = "1"
	
	response = requests.get (
		'https://api.tradier.com/v1/markets/options/chains',
		params = {
			'symbol': symbol, 
			'expiration': expiration, 
			'greeks': 'true'
		},
		headers = {
			'authorization': f'Bearer { authorization }', 
			'Accept': 'application/json'
		}
	)

	json_response = response.json ()
	options_available = json_response ["options"] ["option"];

	try:
		parsed = parse_1.parse (
			symbol,
			options_available, 
			expiration
		)
	
	except Exception as E:
		exception_traceback = traceback.format_exc()
	
		rich.print_json (
			data = {
				"parse exception": {
					"exception": str (E),
					"trace": exception_traceback.split ("\n"),
					"status code": response.status_code
				}
			}
		)
		
		raise Exception (E)

	return parsed