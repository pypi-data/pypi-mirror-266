

'''
	import rollercoaster.treasures.options.movement_calculator as option_movement_calculator
'''

'''
	priorities:
		for one option:
			inputs:
				option type:

				option ask price:	
				option strike price:	
				
				share price:
				
			outputs:
				
'''

'''
	There's 1 inflection point, the break even.
	
		at break even, the multiplier = 1
'''

'''
	ideally, calculate the slope of the line from:
		0 to the break even
		break even to infinity
		
	slope:
		x = share prices
		y = multipliers
		
		= dY / dX 
		
		= (y2 - y1)
		  ---
		  (x2 - x1)
'''

from fractions import Fraction

def calc (
	option_type = "",
	
	option_price = 0,
	strike_price = 0,
	
	share_price = 0
):
	
	#print ()

	expense = option_price
	break_even = option_price + strike_price;
	
	if (share_price <= strike_price):
		# out of the money
		revenue = 0
		
	else:
		# in the money
		revenue = Fraction (share_price) - Fraction (strike_price)

	
	#print ("break even share price:", float (break_even))
	#print ("expense:", float (expense))
	#print ("revenue:", float (revenue))
	
	balance = revenue - expense;
	
	"""
	print ()
	print (
		f'''One "${ 
			float (strike_price)
		}" "{ option_type }" option, bought for "${ 
			float (option_price) 
		}" while shares are "${ 
			float (share_price)
		}" each, yields a balance of "${
			float (balance)
		}".'''
	)
	print ()
	"""
	
	class Movement:
		balance = ""
		
	movement = Movement ()
	movement.balance = balance;
	movement.balance_multiplier = Fraction (revenue, expense);
	movement.break_even = break_even;

	return movement;