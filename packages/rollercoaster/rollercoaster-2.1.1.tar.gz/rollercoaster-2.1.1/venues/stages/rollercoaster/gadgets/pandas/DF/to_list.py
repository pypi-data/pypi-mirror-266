

'''
	from rollercoaster.gadgets.pandas.DF.to_list as DF_to_list
	DF_to_list (DF)
'''

'''
	https://stackoverflow.com/questions/29815129/pandas-dataframe-to-list-of-dictionaries
'''
'''
	import pandas
	catalogue_of_objects = DF.to_dict ('records')
'''

import pandas

def calc (
	df = None
):
	return df.to_dict ('records')
	