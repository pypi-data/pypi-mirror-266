

'''
	import rollercoaster.clouds.Coinbase.API.orders.order_IDs as Coinbase_API_order_IDs
	is_fresh = Coinbase_API_order_IDs.is_fresh (
		order_ID = "",
	
		key_name = ellipsis ["name"],
		key_secret = ellipsis ["privateKey"]
	)
'''

'''
	import rollercoaster.clouds.Coinbase.API.orders.order_IDs as Coinbase_API_order_IDs
	order_IDs = Coinbase_API_order_IDs.proposal (
		key_name = ellipsis ["name"],
		key_secret = ellipsis ["privateKey"]
	)
'''

import rollercoaster.clouds.Coinbase.API as Coinbase_API
from operator import itemgetter

import rich

def proposal (
	key_name = "",
	key_secret = ""
):
	proceeds = Coinbase_API.proposal (
		key_name = key_name,
		key_secret = key_secret,
		
		request_method = "GET",
		request_path = "/api/v3/brokerage/orders/historical/batch",
		request_query_params = ""
	)

	orders = proceeds ["orders"];
	orders = sorted (orders, key = itemgetter ('client_order_id')) 
		
	order_IDs = []
	for order in orders:
		rich.print_json (data = order)
	
		order_IDs.append (order ["client_order_id"])
		
	#order_IDs.sort ()
	
	return order_IDs;
	

def is_fresh (
	key_name = "",
	key_secret = "",
	
	order_ID = ""
):
	order_IDs = proposal (
		key_name = key_name,
		key_secret = key_secret
	)
	
	return order_ID not in order_IDs;