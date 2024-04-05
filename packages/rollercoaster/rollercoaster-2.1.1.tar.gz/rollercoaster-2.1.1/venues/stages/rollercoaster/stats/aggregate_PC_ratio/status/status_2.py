

'''
	python3 insurance.proc.py "stats/aggregate_PC_ratio/status/status_2.py"
'''

'''
	SOURCES:
		https://www.nasdaq.com/market-activity/stocks/fslr/option-chain
'''


import rollercoaster.stats.aggregate_PC_ratio as aggregate_PC_ratio


import ships.paths.files.scan.JSON as scan_JSON_path


import pathlib
from os.path import dirname, join, normpath
import sys
this_dir = pathlib.Path (__file__).parent.resolve ()

def check_1 ():
	example = scan_JSON_path.start (normpath (join (this_dir, "examples/2.JSON")))
	evaluation = aggregate_PC_ratio.calc (example)
	
	import json
	print ("evaluation:", json.dumps (evaluation, indent = 4))

	assert (evaluation ["expirations"][0]["sums"]["puts"]["ask"] == 2000)
	assert (evaluation ["expirations"][0]["sums"]["puts"]["bid"] == 1200)
	assert (evaluation ["expirations"][0]["sums"]["puts"]["last"] == 0)

	assert (evaluation ["expirations"][0]["sums"]["calls"]["ask"] == 2000)
	assert (evaluation ["expirations"][0]["sums"]["calls"]["bid"] == 1700)
	assert (evaluation ["expirations"][0]["sums"]["calls"]["last"] == 3600)

	assert (evaluation ["expirations"][0]["PC ratios"]["ask"] == [ 1, 1 ])
	assert (evaluation ["expirations"][0]["PC ratios"]["bid"] == [ 1, 1.4166666666666667 ])
	assert (evaluation ["expirations"][0]["PC ratios"]["last"] == [ "?", "?" ])

	assert (evaluation ["PC ratios"]["ask"] == [ 1, 1 ])
	assert (evaluation ["PC ratios"]["bid"] == [ 1, 1.4166666666666667 ])
	assert (evaluation ["PC ratios"]["last"] == [ "?", "?" ])

	assert (evaluation ["sums"]["puts"]["ask"] == 2000)
	assert (evaluation ["sums"]["puts"]["bid"] == 1200)
	assert (evaluation ["sums"]["puts"]["last"] == 0)

	assert (evaluation ["sums"]["calls"]["ask"] == 2000)
	assert (evaluation ["sums"]["calls"]["bid"] == 1700)
	assert (evaluation ["sums"]["calls"]["last"] == 3600)

	return;
	
	
checks = {
	"check 1": check_1
}