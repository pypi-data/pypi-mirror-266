
'''
	import rollercoaster.rides.season_1.ATR.ChatGPT_ATR_1 as ChatGPT_ATR_1
	ChatGPT_ATR_1.calculate_ATR ()
	
	# Example usage:
	# data = [
	#     {'high': 50, 'low': 45, "close": 48},
	#     {'high': 55, 'low': 50, "close": 52},
	#     # ... (more data)
	# ]
	# calculate_ATR(data, period=14)
	# print(data)
'''

'''
Can you provide me with
the ATR formula in python3 without pandas 
with input as a list of dicts, 
that adds ATR and atr to the dicts in the input list,
and the input values are "high", "low", and "close",
with the licensing info written as a comment?
where the name of the def is calculate_ATR

Where the license says:
"copyright ChatGPT and OpenAI"
"This work is subject to the terms of this custom license that is a fork of the MIT license."
Where the license is a custom version of the MIT license
that doesn't use any all caps writing?

After the license can you say, "These licensing terms were provided as per an ask."

And can you please reference any sources utilized?
'''
# Custom License (Fork of MIT License)

# Copyright (c) ChatGPT and OpenAI

# This work is subject to the terms of this custom license that is a fork of the MIT license.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "software"), to deal
# in the software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the software, and to permit persons to whom the software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the software.

# The software is provided "as is," without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose, and noninfringement. In no event shall the
# authors or copyright holders be liable for any claim, damages, or other
# liability, whether in an action of contract, tort or otherwise, arising from,
# out of or in connection with the software or the use or other dealings in
# the software.

# These licensing terms were provided as per an ask.

def calculate_ATR(data, period=14):
    tr_list = []
    atr_list = []

    for i in range(1, len(data)):
        tr = max(
            data[i]['high'] - data[i]['low'],
            abs(data[i]['high'] - data[i - 1]["close"]),
            abs(data[i]['low'] - data[i - 1]["close"])
        )
        tr_list.append(tr)

	# Initial ATR value
	ATR_1 = sum (
		tr_list [:period]
	) / period
	
    atr_list.append (ATR_1)  

    for i in range (period, len (tr_list)):
        atr_value = (
			(period - 1) * atr_list [-1] + tr_list [i]
		) / period
        
		atr_list.append (atr_value)

    for i in range(len(atr_list)):
        data [i] ['ATR'] = atr_list[i]


