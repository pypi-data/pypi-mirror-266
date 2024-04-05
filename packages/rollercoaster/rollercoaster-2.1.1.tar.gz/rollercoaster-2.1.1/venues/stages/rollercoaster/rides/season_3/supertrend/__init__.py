

'''
	import rollercoaster.rides.season_3.supertrend as supertrend
	DF ['supertrend'] = supertrend.calc (DF)
'''


import pandas as pd
import numpy as np

def calc (data, period=7, multiplier=3):
    high = data['high']
    low = data['low']
    close = data['close']

    atr = pd.Series(index=high.index)
    atr[0] = 0

    # Calculate Average True Range (ATR)
    for i in range(1, len(atr)):
        tr = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
        atr[i] = (atr[i - 1] * (period - 1) + tr) / period

    # Calculate SuperTrend
    upper_band = (high + low) / 2 + multiplier * atr
    lower_band = (high + low) / 2 - multiplier * atr

    supertrend = pd.Series(index=close.index)
    supertrend[0] = 0

    for i in range(1, len(supertrend)):
        if close[i - 1] <= supertrend[i - 1]:
            supertrend[i] = upper_band[i]
        else:
            supertrend[i] = lower_band[i]

    return supertrend

