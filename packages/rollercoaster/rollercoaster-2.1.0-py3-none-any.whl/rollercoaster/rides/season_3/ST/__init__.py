
'''
	import rollercoaster.rides.season_3.ST as ST_tap
	ST_tap.calc (places, length = 50, multiplier = 2.0)
'''

'''
	import rollercoaster.rides.season_3.ST as ST_tap
	ST_tap.plot (chart, DF, ST_direction)
'''

import ccxt
import ships.flow.demux_mux2 as demux_mux2
from pprint import pprint
import datetime
import rich
import arrow
import json
import ccxt
import pandas
import pandas_ta
import plotly.graph_objects as go

def calc (
	OHLCV_DF,
	length = 50,
	multiplier = 2.0
):
	ST_direction = f"SUPERTd_{ str (length) }_{ str (multiplier) }"

	supertrend_DF = pandas_ta.supertrend (
		OHLCV_DF ['high'], 
		OHLCV_DF ['low'], 
		OHLCV_DF ['close'], 
		
		length = length, 
		multiplier = multiplier
	)
	
	class Proceeds:
		def __init__ (this, DF, direction):
			this.DF = DF
			this.direction = direction
			
	return Proceeds (
		supertrend_DF,
		ST_direction
	)	

	
def plot (
	chart,
	DF_2,
	ST_direction
):


	'''
		Super Trend,
			Color of candles
	'''
	'''
	import numpy
	chart.add_trace (
		go.Scatter (
			x = DF_2 ['UTC date string'],
			y = DF_2 ["close"],
			
			marker_color = numpy.select (
				[
					DF_2 [ ST_direction ] == -1, 
					DF_2 [ ST_direction ] == 1
				], 
				[ "orange", "purple" ], 
				"rgba(0,0,0,0)"
			),
			
			mode = "markers",
			#marker_color = "black",
			yaxis = "y2",
			name = "Bubble"
		),
		row = 1, 
		col = 1
	)
	'''
	
	amounts = []
	
	previous = None
	for index, row in DF_2.iterrows ():
		direction = row [ ST_direction ]
		UTC_date_string = row ['UTC date string']

		chart.add_annotation(
			x = row ['UTC date string'], 
			y = 0.35, 
			
			xref = 'x', 
			yref = 'paper',
			xanchor = 'left',
			
			showarrow = False, 
			 
			text = row [ ST_direction ]
		)

		if (previous in [ -1, 1 ] and direction != previous):		
			if (row [ ST_direction ] == 1):
				text = 'rich'
			else:
				text = 'poor'
				
			chart.add_annotation(
				x = row ['UTC date string'], 
				y = 0.15, 
				
				xref = 'x', 
				yref = 'paper',
				xanchor = 'left',
				
				showarrow = False, 
				 
				text = row [ ST_direction ]
			)
			
			amounts.append ([ 
				previous * -1,
				row ["close"]
			])
			
			print (
				"change of direction:", 
				previous * -1, 
				row ['UTC date string'], 
				row ["close"]
			)
			
			'''
			marker_color = numpy.select (
					[
						DF_2 [ ST_direction ] == -1, 
						DF_2 [ ST_direction ] == 1
					], 
					[ "orange", "purple" ], 
					"rgba(0,0,0,0)"
				),
			'''
			
			'''
			chart.add_shape (
				x0 = DF_2 ['UTC date string'],
				
				
				y = DF_2 ["close"],
				
				marker_color = "orange",
				
				mode = "markers",
				#marker_color = "black",
				yaxis = "y2",
				name = "Bubble"
			)
			'''
			
			chart.add_shape (
				type = "rect",
				xref = "x", 
				yref = "y",

				x1 = row ['UTC date string'],
				x0 = row ['UTC date string'], 
				
				y1 = row ['close'] + .1,
				y0 = row ['close'],
			
				line = dict (
					color = "RoyalBlue",
					width = 3,
				),
				
				fillcolor="LightSkyBlue",
			);
			
			chart.add_annotation(
				x = row ['UTC date string'], 
				y = 0.05, 
				
				xref = 'x', 
				yref = 'paper',
				xanchor = 'left',
				
				showarrow = False, 
				 
				text = text
			)
			
		
		
		previous = direction;
		



	win_rate (amounts)

	print (f"[{ UTC_date_string }]", direction)
	
	
def win_rate (amounts):
	fractional_commision = 1/100;

	money = 1
	
	trade_count = 0
	
	add_to_trade_count = False;
	
	last_index = len (amounts) - 1
	s = 1
	while (s <= last_index):
		amount = amounts [s]
		
		direction = amount [0]
		
		price_1 = amounts [s - 1] [1]
		price_2 = amount [1]
		
		if (direction == -1):
			print ("[span] holding shares")
		
			add_to_trade_count = True;
		
			incline_change = (price_2 / price_1)
		
			m1 = money;
			money = money * incline_change
			print ("	money:", m1, "->", money)
		else:
			print ("[span] not holding shares")	
			
		if (add_to_trade_count):
				
		
			#print ("	trade_count += 1", amount) 
			trade_count += 1
		
		
		#print (amount)
	
		
	
		s += 1

	print ()
	print ("money:", money)
	print ("trade_count:", trade_count)
	print ()

	return;