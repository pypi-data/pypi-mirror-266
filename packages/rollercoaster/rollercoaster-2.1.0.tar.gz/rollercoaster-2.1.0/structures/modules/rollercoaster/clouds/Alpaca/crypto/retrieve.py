
'''
	#
	#	This is alpaca crypto data
	#

	import datetime
	from alpaca.data.timeframe import TimeFrame
	import rollercoaster.clouds.Alpaca.crypto.retrieve as retrieve_Alpaca_shares
	retrieve_Alpaca_shares.wonderfully (
		span = [
			datetime.datetime (2023, 11, 28),
			datetime.datetime (2023, 12, 2)
		],
		interval = TimeFrame.Day,
		symbol_or_symbols = [ "BTC/USD" ]
	)
'''



import datetime
import json

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

def wonderfully (
	span = [
		datetime.datetime (2023, 11, 28),
		datetime.datetime (2023, 12, 2)
	],
	interval = TimeFrame.Day,
	symbol_or_symbols = [ "BTC/USD" ]
):
	client = CryptoHistoricalDataClient ()

	request_params = CryptoBarsRequest (
		symbol_or_symbols = ["BTC/USD"],
		timeframe = interval,
		start = span [0],
		end = span [1]
	)

	shares = client.get_crypto_bars (request_params)

	return shares