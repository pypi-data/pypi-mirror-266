
'''
	import rollercoaster.clouds.Coinbase.API.accounts as Coinbase_API_accounts
	proceeds = Coinbase_API_accounts.proposal (
		key_name = ellipsis ["name"],
		key_secret = ellipsis ["privateKey"],
		
		request_path = "/api/v3/brokerage/accounts"
	)

	for account in accounts:
		print ("name:", account ["name"]);
'''


import rollercoaster.clouds.Coinbase.API as Coinbase_API
from operator import itemgetter

def proposal (
	key_name = "",
	key_secret = "",
	request_path = ""
):
	proceeds = Coinbase_API.proposal (
		key_name = key_name,
		key_secret = key_secret,
		
		request_path = request_path
	)

	accounts = proceeds ["accounts"];
	accounts = sorted (accounts, key = itemgetter ('name')) 
		
	return accounts;