

'''
	import ccxt
	print ('CCXT Version:', ccxt.__version__)
	
	symbol = "BTC/USDT"
	
	exchange = ccxt.kraken ()
	#exchange = ccxt.coinbase ()
	#exchange = ccxt.cryptocom ()

	import rollercoaster.clouds.CCXT.OHLCV as CCXT_OHLCV_intervals
	CCXT_OHLCV_intervals.retrieve (
		symbol = symbol,
		exchange = exchange,
		from_time = int (
			datetime.datetime.strptime (
				"2023-12-25 20:00:00+00:00", 
				"%Y-%m-%d %H:%M:%S%z"
			).timestamp () * 1000
		)
	)
'''

import arrow

def retrieve (
	symbol = None,
	exchange = "",
	limit = 100,
	from_time = "",
	
	span = '15m'
):	
	response = exchange.fetch_ohlcv (
		symbol, 
		span, 
		from_time,
		limit = limit
	)
	
	#pprint (response)

	parsed = []
	for interval in response:	
		UTC_date_string = arrow.get (interval [0]).datetime.isoformat ();
	
		parsed.append ({
			"UTC timestamp": interval [0],
			"UTC date string": UTC_date_string,
			
			"open": interval [1],
			"high": interval [2],
			"low": interval [3],
			"close": interval [4],
			"volume": interval [5]
		})

	return parsed