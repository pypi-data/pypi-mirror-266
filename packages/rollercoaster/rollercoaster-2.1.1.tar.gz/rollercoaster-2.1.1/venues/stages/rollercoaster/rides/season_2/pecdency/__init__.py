


def calc (places, spans=14, multiplier=2.0):
	atr_values = []
	upper_band_values = []
	lower_band_values = []
	pecdency_values = []

	atr = 0
	upper_band = 0
	lower_band = 0
	pecdency = 0

	for i, candle in enumerate(places):
		high = candle['high']
		low = candle['low']
		close = candle['close']

		

		tr = max(high - low, abs(high - close), abs(low - close))

		if i == 0:
			atr = tr
			upper_band = high + multiplier * atr
			lower_band = low - multiplier * atr
		else:
			atr = ((spans - 1) * atr + tr) / spans
			upper_band = high + multiplier * atr
			lower_band = low - multiplier * atr

		pecdency_1 = ((high + low) / 2) + (multiplier * atr)


		if i == 0 or places [i - 1] ['close'] <= pecdency:
			pecdency = upper_band
		else:
			pecdency = lower_band

		atr_values.append(atr)
		upper_band_values.append(upper_band)
		lower_band_values.append(lower_band)
		pecdency_values.append(pecdency)

		candle ['ATR'] = atr
		candle ['pecdency UB'] = upper_band
		candle ['pecdency LB'] = lower_band
		candle ['pecdency'] = pecdency
		candle ['pecdency 1'] = pecdency_1

	return places