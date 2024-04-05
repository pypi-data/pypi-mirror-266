
'''
	import rollercoaster.stats.aggregate_break_even.show as show_aggregate_break_even
	show_aggregate_break_even.data (proceeds)
'''

'''
	expiration	"calls ask aggregate BE"

'''

import numpy
import pandas
		
		
def data (proceeds):
	expirations = proceeds ["expirations"]
	
	columns = [
		'expiration',
		'"calls ask aggregate BE"',
		'"calls ask aggregate BE multiplier"',
		'"puts ask aggregate BE"',
		'"puts ask aggregate BE multiplier"',
	]
	
	fields = []
	for expiration in expirations:
		fields.append ([
			expiration ["expiration"],
			
			expiration ["aggregate break even"] ["calls"] ["ask"],	
			expiration ["aggregate multiplier"] ["calls"] ["ask"],
			
			expiration ["aggregate break even"] ["puts"] ["ask"],		
			expiration ["aggregate multiplier"] ["puts"] ["ask"]			
		])
	
	df = pandas.DataFrame (
		numpy.array (fields),
		columns = columns
	)
	
	print (df)

	return;