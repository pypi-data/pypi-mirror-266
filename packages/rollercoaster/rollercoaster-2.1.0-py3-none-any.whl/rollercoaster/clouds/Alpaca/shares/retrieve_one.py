


'''

	itinerary:

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
	return;