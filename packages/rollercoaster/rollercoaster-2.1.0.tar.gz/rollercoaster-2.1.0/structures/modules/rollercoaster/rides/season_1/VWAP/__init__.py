

'''
	import rollercoaster.rides.season_1.VWAP as VWAP
	DF ['VWAP'] = VWAP.calc (DF)
'''

import pandas as pd

def calc (
	data, 
	price_column = 'close', 
	volume_column = 'volume'
):   
	typical_price = (data['high'] + data['low'] + data[price_column]) / 3

	# Calculate the product of typical price and volume
	tpv = typical_price * data [volume_column]

	# Calculate the cumulative sum of (typical price * volume)
	cum_tpv = tpv.cumsum ()

	# Calculate the cumulative sum of volume
	cum_volume = data[volume_column].cumsum()

	# Calculate VWAP
	vwap = cum_tpv / cum_volume

	return vwap

