
'''
	python3 insurance.proc.py 'gadgets/pandas/df/_status/status_from_1.py'
'''

import rollercoaster.gadgets.pandas.DF.from_list as df_from_list
import rollercoaster.gadgets.pandas.DF.to_list as df_to_list

def check_1 ():	
	original_list =  [{
		"open": 10,
		"close": 11,
		"high": 20,
		"low": 9
	}]

	df = df_from_list.calc (
		list = [{
			"open": 10,
			"close": 11,
			"high": 20,
			"low": 9
		}]
	)
	
	steps = df_to_list.calc (df)
		
	assert (
		original_list ==
		steps
	)
	
checks = {
	'check 1': check_1
}