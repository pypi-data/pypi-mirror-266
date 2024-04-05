

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
	example = scan_JSON_path.start (normpath (join (this_dir, "examples/1.JSON")))
	proceeds = aggregate_PC_ratio.calc (example)
	
	import json
	print ("proceeds:", json.dumps (proceeds, indent = 4))

	return;
	
	
checks = {
	"check 1": check_1
}