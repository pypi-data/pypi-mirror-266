

'''
	import rollercoaster.clouds.Coinbase.API.build_JWT as Coinbase_API_JWT
	JWT = Coinbase_API_JWT.build (
		key_name = ellipsis ["name"],
		key_secret = ellipsis ["privateKey"],
		
		request_path = "/api/v3/brokerage/accounts"
	)

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
def build (
	key_name = "",
	key_secret = "",

	request_method = "GET",
	request_host = "api.coinbase.com",
	request_path = "/api/v3/brokerage/accounts",
	
	service_name = "retail_rest_api_proxy"
):
	def build_jwt (service, uri):
		private_key_bytes = key_secret.encode('utf-8')
		private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
		jwt_payload = {
			'sub': key_name,
			'iss': "coinbase-cloud",
			'nbf': int(time.time()),
			'exp': int(time.time()) + 60,
			'aud': [ 
				service
			],
			'uri': uri,
		}
		
		rich.print_json (data = jwt_payload)
		
		jwt_token = jwt.encode(
			jwt_payload,
			private_key,
			algorithm='ES256',
			headers={'kid': key_name, 'nonce': secrets.token_hex()},
		)
		
		rich.print_json (data = jwt_token)
		
		
		return jwt_token
	
	

	def proposal (
		method = "GET",
		route = "",
		
		payload = "",

		Authorization = ""
	):
		conn = http.client.HTTPSConnection (request_host)
		
		payload = json.dumps (payload)
		
		headers = {
			'Content-Type': 'application/json',
			'Authorization': Authorization
		}
		
		conn.request (
			method, 
			route, 
			payload, 
			headers
		)
		
		res = conn.getresponse()
		data = res.read()
		
		return {
			"data": data.decode("utf-8")
		}
	
	
	URI = f"{request_method} {request_host}{request_path}"
	JWT = build_jwt (service_name, URI)
	print(f"export JWT={JWT}")

	print (f"""
	
	curl -H "Authorization: Bearer { JWT }" 'https://api.coinbase.com/api/v3/brokerage/accounts'	
	
	""")

	
	return JWT;



