import math
import pandas as pd
import numpy as np
from scipy import constants


def simple_scattering(df_current, revolution_freq):
	"""
	Расчет времени жизни пучка через экспоненциальный распад
	с учетом миллисекундного разрешения временных меток
	
	Параметры:
	df_current - DataFrame с данными о токе
	revolution_freq - частота обращения частиц [Гц]
	
	Возвращает:
	Series с временем жизни в часах
	"""
	df = df_current.copy()
	# Конвертируем ток в число частиц
	df['N'] = df_current['value'] / (constants.e * revolution_freq)
	
	# Вычисляем разницу между текущим и предыдущим значением
	df['delta_t'] = df_current['timestamp'].diff().dt.total_seconds()
	
	# Расчет tau по формуле: N_curr = N_0 * exp(-Δt/τ)
	with np.errstate(divide='ignore', invalid='ignore'):
		df['tau'] = -df['delta_t'] / np.log(df['N'] / df['N'].shift(1))
	
	# Переводим секунды в часы и убираем выбросы
	df['tag'] = "calculated_lifetime"
	df['value'] = df['tau'] / 3600
	df['value'] = df['value'].where(df['value'].between(0, 1000))  # Фильтр нереальных значений
	
	return df