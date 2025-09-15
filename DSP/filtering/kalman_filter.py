import numpy as np
import pandas as pd

def exponential_decay_scattering(n1, n2, delta_t):
	# tan = (n2 - n1) / delta_t
	# return n2 * tan
	ratio = n2 / n1
	return n2 * ratio

def kalman_filter_exp_decay(signal, q=0.001, r=0.1):
		x_prev_prev = signal[0] 
		x_prev = signal[0]  
		p = 1.0

		result = []

		for value in signal:
			x_pred = exponential_decay_scattering(x_prev_prev, x_prev, 1)
			p_pred = p + q

			k = p_pred / (p_pred + r)
			x = x_pred + k * (value - x_pred)
			p = (1 - k) * p_pred
			
			result.append(x)

			x_prev_prev = x_prev
			x_prev = x

		return pd.Series(result)


