

'''
	import ccxt
	import rollercoaster.clouds.CCXT.symbols.array as CCXT_symbols

	symbols = CCXT_symbols.retrieve (
		exchange = ccxt.kraken ()
	)
'''


def retrieve (
	exchange = ""
):
	symbols = exchange.symbols;
	markets = exchange.load_markets ()
	symbols_list = []
	for market in markets:
		symbols_list.append (markets [market] ["id"])
		
	return symbol