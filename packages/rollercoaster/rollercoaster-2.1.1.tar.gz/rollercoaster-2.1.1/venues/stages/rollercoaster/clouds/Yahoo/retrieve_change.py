
'''
	from datetime import datetime, timedelta
	import rollercoaster.clouds.Yahoo.retrieve_change as Yahoo_retrieve_change
	change = Yahoo_retrieve_change.perfectly (
		symbol = "JETS",
		date_1 = datetime.today () - timedelta (days = 10),,
		date_2 = datetime.today ()
	)
'''



from datetime import datetime, timedelta
import yfinance
from fractions import Fraction

def retrieve (symbol, date):
	ticker = yfinance.Ticker (symbol);
	historical_data = ticker.history (
		start = (date - timedelta (days = 1)).strftime ('%Y-%m-%d'), 
		end = date.strftime ('%Y-%m-%d')
	)
	
	price = None;
	try:
		#price = historical_data ['Close'][0]
		price = historical_data.iloc[0] ['Close']
	except Exception as E:
		print (E)

	return Fraction (price)

def perfectly (
	symbol = "",
	date_1 = None,
	date_2 = None
):	
	price_1 = retrieve (symbol, date_1)
	price_2 = retrieve (symbol, date_2)

	print (price_1, price_2)

	return price_2 / price_1