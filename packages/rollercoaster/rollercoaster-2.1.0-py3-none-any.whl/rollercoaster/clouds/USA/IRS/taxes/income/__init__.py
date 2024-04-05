


'''
	agenda:
	
		import rollercoaster.groups.USA.taxes.income as USA_income_taxes
		USA_income_taxes.calc (
			year = "",
			income = ""
		)
'''


years = [{
	"year": 2024
},{
	"year": 2023
},{
	"year": 2022,
	"brackets": [
		[ 10275, 10 ],
		[ 41775, 12 ],
		[ 89075, 22 ],
		[ 170050, 24 ],
		[ 215950, 32 ],
		[ 539900, 35 ],
		[ float ('inf'), 37 ]
	]
}]

def calc (
	year = "",
	income = ""
):
	return;