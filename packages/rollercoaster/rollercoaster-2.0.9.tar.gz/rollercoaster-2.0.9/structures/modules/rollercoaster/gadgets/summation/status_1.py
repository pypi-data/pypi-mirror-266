



'''
	python3 insurance.proc.py gadgets/summation/status_1.py
'''

from rollercoaster.gadgets.summation import summation
	


from rich import print_json

def check_1 ():	
	def formula (s):
		return s

	proceeds = summation (
		start = 1,
		end = 3,
		formula = formula
	)
	
	assert (proceeds == 6)

	print ("proceeds:", proceeds)

	return;
	
checks = {
	'check 1': check_1
}