

'''

'''

import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime, timedelta
import yfinance as yf

class Strategy_1 (bt.Strategy):
	def __init__(self):
		# Keep a reference to the "close" line in the data[0] dataseries
		self.dataclose = self.datas[0].close

		# To keep track of pending orders
		self.order = None
		
		#bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
		#bt.indicators.WeightedMovingAverage(self.datas[0], period=25).subplot = True
		#bt.indicators.StochasticSlow(self.datas[0])
		#bt.indicators.MACDHisto(self.datas[0])
		#rsi = bt.indicators.RSI(self.datas[0])
		#bt.indicators.SmoothedMovingAverage(rsi, period=10)
		#bt.indicators.ATR(self.datas[0]).plot = False

	'''
	
	'''
	def log (self, txt, dt=None):
		''' Logging function fot this strategy'''
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	

	def notify_order (self, order):
		if order.status in [ order.Submitted, order.Accepted ]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [ order.Completed ]:
			if order.isbuy ():
				self.log ('pump occurred, %.2f' % order.executed.price)
			
			elif order.issell ():
				self.log ('dump occurred, %.2f' % order.executed.price)

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		# Write down: no pending order
		self.order = None


	'''
	
	'''
	def next (self):
		# Simply log the closing price of the series from the reference
		self.log ('Close, %.2f' % self.dataclose[0])

		
		'''
			if an order is pending, a second one cannot be sent
		'''
		if self.order:
			return

		# Check if we are in the market
		if not self.position:

			# Not yet ... we MIGHT BUY if ...
			if self.dataclose[0] < self.dataclose[-1]:
				# current close less than previous close

				if self.dataclose[-1] < self.dataclose[-2]:
					# previous close less than the previous close

					# BUY, BUY, BUY!!! (with default parameters)
					self.log ('creating a pump, %.2f' % self.dataclose[0])

					# Keep track of the created order to avoid a 2nd order
					self.order = self.buy ()

		else:
			# Already in the market ... we might sell
			if len (self) >= (self.bar_executed + 5):
				self.log ('creating a dump, %.2f' % self.dataclose[0])

				# Keep track of the created order to avoid a 2nd order
				self.order = self.sell ()



