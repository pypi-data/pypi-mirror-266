

'''
	RSI
'''
'''
	import rollercoaster.rides.season_1.RSI as RSI
	DF ['RSI'] = RSI.calc (DF)
'''

import pandas as pd
import numpy as np

def calc (
	data, 
	column_name = 'close', 
	period = 14
):


	# Calculate daily price changes
    delta = data [ column_name ].diff (1)

    # Calculate gains (positive changes) and losses (negative changes)
    gains = delta.where (delta > 0, 0)
    losses = -delta.where (delta < 0, 0)

    # Calculate average gains and losses over the specified period
    avg_gain = gains.rolling (window = period, min_periods = 1).mean ()
    avg_loss = losses.rolling (window = period, min_periods = 1).mean ()

    # Calculate relative strength (RS)
    RS = avg_gain / avg_loss

    # Calculate RSI
    RSI = 100 - (100 / (1 + RS))

    return RSI

