
'''
//
//  This derivative is subject to the same terms as the integral.
//
//      Previous version:
//          This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) https://creativecommons.org/licenses/by-nc-sa/4.0/
//          © alexgrover
//
'''

'''
	import rollercoaster.rides.season_4.AO as AO
	
	data = AO.calc ([{
		"high": "",
		"low": "",
		"open": "",
		"close": ""
	}])	
'''



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calc (data, length=50, signal_length=9):
    alpha = 2 / (length + 1)

    increase_1 = 0.0
    increase_2 = 0.0
    decrease_1 = 0.0
    decrease_2 = 0.0

    incline_components = []
    decline_components = []

    for i in range(len(data)):
        C = data['close'][i]
        O = data['open'][i]

        increase_1 = max(C, O, increase_1 - (increase_1 - C) * alpha)
        increase_2 = max(C * C, O * O, increase_2 - (increase_2 - C * C) * alpha)
        decrease_1 = min(C, O, decrease_1 + (C - decrease_1) * alpha)
        decrease_2 = min(C * C, O * O, decrease_2 + (C * C - decrease_2) * alpha)

        incline_component = np.sqrt(decrease_2 - decrease_1 * decrease_1)
        decline_component = np.sqrt(increase_2 - increase_1 * increase_1)

        incline_components.append(incline_component)
        decline_components.append(decline_component)

    incline_components = pd.Series(incline_components, name='Incline Component')
    decline_components = pd.Series(decline_components, name='Decline Component')

    signal = pd.Series(np.maximum(incline_components, decline_components).ewm(span=signal_length).mean(), name='Signal')

    return incline_components, decline_components, signal

# Example usage:
# Assuming you have a DataFrame 'df' with 'open' and 'close' columns.
# df = ...

