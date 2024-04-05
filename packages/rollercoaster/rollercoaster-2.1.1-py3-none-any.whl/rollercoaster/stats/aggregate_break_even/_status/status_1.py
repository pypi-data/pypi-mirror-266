

'''
	python3 status.py 'stats/aggregate_break_even/_status/status_1.py'
'''

'''
	sources:
		https://www.nasdaq.com/market-activity/stocks/fslr/option-chain
'''


import ships.paths.files.scan.JSON as scan_JSON_path
import rollercoaster.stats.aggregate_break_even as aggregate_break_even
import rollercoaster.stats.aggregate_break_even.show as show_aggregate_break_even
	
import pathlib
from os.path import dirname, join, normpath
import sys
this_dir = pathlib.Path (__file__).parent.resolve ()

def check_1 ():
	example = scan_JSON_path.start (normpath (join (this_dir, "examples/0.JSON")))
	proceeds = aggregate_break_even.calc (example)
	
	import json
	print ("proceeds:", json.dumps (proceeds, indent = 4))

	show_aggregate_break_even.data (proceeds)

	assert (
		proceeds ==
		{
			"expirations": [
				{
					"expiration": "2023-10-13",
					"aggregate break even": {
						"calls": {
							"ask": "15.857142857142858",
							"bid": "15.857142857142858",
							"last": "15.857142857142858"
						},
						"puts": {
							"ask": "14.142857142857142",
							"bid": "14.142857142857142",
							"last": "14.142857142857142"
						}
					},
					"aggregate multiplier": {
						"calls": {
							"ask": "1.2738095238095237",
							"bid": "1.2738095238095237",
							"last": "1.2738095238095237"
						},
						"puts": {
							"ask": "1.2026862026862026",
							"bid": "1.2026862026862026",
							"last": "1.2026862026862026"
						}
					}
				}
			]
		}
	)
	
	
checks = {
	"check 1": check_1
}