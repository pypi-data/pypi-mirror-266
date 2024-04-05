



'''
	from operator import itemgetter
	import rollercoaster.clouds.Coinbase.API.products.catalogue as Coinbase_API_products_catalogue
	products = Coinbase_API_products_catalogue.proposal (
		key_name = ellipsis ["name"],
		key_secret = ellipsis ["privateKey"]
	)

	product_IDs = []
	for product in products:
		if (not product ["product_id"].endswith ("-USD")):
			continue;

		product_IDs.append (product ["product_id"])
		continue;

		#print ("product_id:", product ["product_id"]);
		rich.print_json (data = product)
	#

	print (product_IDs)
'''


import rollercoaster.clouds.Coinbase.API as Coinbase_API
from operator import itemgetter

def proposal (
	key_name = "",
	key_secret = "",
	
	request_path = "/api/v3/brokerage/products"
):
	proceeds = Coinbase_API.proposal (
		key_name = key_name,
		key_secret = key_secret,
		
		request_path = request_path
	)

	products = proceeds ["products"];
	products = sorted (products, key = itemgetter ('name')) 
		
	return products;