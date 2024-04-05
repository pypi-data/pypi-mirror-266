

'''
	import rollercoaster.clouds.Coinbase.API as Coinbase_API
	proceeds = Coinbase_API.proposal (
		key_name = ellipsis ["name"],
		key_secret = ellipsis ["privateKey"],
		
		request_path = "/api/v3/brokerage/accounts"
	)
	
	from operator import itemgetter
	accounts = proceeds ["accounts"];
	accounts = sorted (accounts, key=itemgetter('name')) 

	for account in accounts:
		print ("name:", account ["name"]);

'''

'''
	https://docs.cloud.coinbase.com/exchange/docs/sandbox
	https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder
'''

import rich
import jwt
from cryptography.hazmat.primitives import serialization
import time
import secrets
import http.client
import json
def proposal (
	key_name = "",
	key_secret = "",

	request_method = "GET",
	request_host = "api.coinbase.com",
	request_path = "/api/v3/brokerage/accounts",
	request_body = "",
	request_query_params = "",

	service_name = "retail_rest_api_proxy",
):
	def build_jwt (service, uri):
		private_key_bytes = key_secret.encode('utf-8')
		private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
		jwt_payload = {
			'sub': key_name,
			'iss': "coinbase-cloud",
			'nbf': int(time.time()),
			'exp': int(time.time()) + 60,
			'aud': [service],
			'uri': uri,
		}
		
		#rich.print_json (data = jwt_payload)
		
		jwt_token = jwt.encode(
			jwt_payload,
			private_key,
			algorithm='ES256',
			headers={'kid': key_name, 'nonce': secrets.token_hex()},
		)
		
		#rich.print_json (data = jwt_token)
		
		
		return jwt_token
	
	

	def proposal (
		method = "GET",
		route = "",
		
		payload = "",

		Authorization = ""
	):
		conn = http.client.HTTPSConnection (request_host)
		
		headers = {
			'Content-Type': 'application/json',
			'Authorization': Authorization
		}
		
		#print ("payload:", payload)
		
		conn.request (
			method, 
			route + request_query_params, 
			payload, 
			headers
		)
		
		res = conn.getresponse ()		
		print ("response status:", res.status)
		
		data = res.read ()
		#print ("response data:", data)
		
		
		return {
			"data": data.decode ("utf-8")
		}
	
	
	URI = f"{request_method} {request_host}{request_path}"
	JWT = build_jwt (service_name, URI)
	#print(f"export JWT={JWT}")


	rich.print_json (data = {
		"method": request_method,
		"route": request_path,
		
		"payload": request_body,

		"Authorization": f"Bearer { JWT }"
	})
	
	proceeds = proposal (
		method = request_method,
		route = request_path,
		
		payload = request_body,

		Authorization = f"Bearer { JWT }"
	)
	
	if ("data" not in proceeds):
		print ("proceeds:", proceeds)
	
	#print (proceeds ["data"])
	#rich.print_json (data = json.loads (proceeds ["data"]))
	
	return json.loads (proceeds ["data"])
