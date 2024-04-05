
'''
	python3 insurance_clouds.proc.py "clouds/Alpaca/crypto/_status/API_status_1.py"
'''

import datetime
from alpaca.data.timeframe import TimeFrame
import rollercoaster.clouds.Alpaca.crypto.structure_1 as structure_1
from rich import print_json

def check_1 ():
	intervals = structure_1.calculate (
		span = [
			datetime.datetime (2023, 11, 28),
			datetime.datetime (2023, 12, 2)
		],
		interval = TimeFrame.Day,
		symbol_or_symbols = [ "BTC/USD" ]
	)
	
	assert (len (intervals) == 4)
	
	for interval in intervals:
		assert ("open" in interval)		
		assert ("close" in interval)
		
		assert ("high" in interval)		
		assert ("low" in interval)
		
		assert ("volume" in interval)
	
	
	print_json (data = intervals)
	
	return;
	
	
checks = {
	'check 1': check_1
}