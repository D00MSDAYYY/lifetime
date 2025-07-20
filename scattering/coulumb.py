import math
import pandas as pd
import CONSTANTS

from scipy import constants

def coulomb_scattering_wiedermann(beta, P_Torr, z, Z, p, theta_max):
	"""
	Вычисляет время жизни пучка из-за рассеяния на остаточном газе в системе CGS.
	
	Параметры:
	beta : отношение скорости частиц к скорости света [безразмерно]
	P_Torr : давление газа [Торр]
	z : заряд ускоряемой частицы (для электрона z=1)
	Z : заряд ядра атома газа (для N₂ Z=7)
	p : импульс пучка [г·см/с]
	theta_max : максимальный угол рассеяния [радианы]

	Возвращает:
	tau_hours : время жизни [часы]
	"""

	# Расчёт компонентов формулы
	paren = (z * Z * CONSTANTS.CGS.e**2 / (2 * beta * CONSTANTS.CGS.c * p))**2
	tmp = CONSTANTS.CGS.c * beta * constants.Avogadro * P_Torr / 760 * ( paren ) * 4 * math.pi / (math.tan(theta_max / 2)**2)
	tau = 1 / tmp

	tau_hours = tau / 3600  # Перевод в часы

	return tau_hours


def coulumb_scattering_zaycev(df_current, revolution_freq, beta, P_Torr, z, Z, p, theta_max): 
	
	df = df_current.copy()
	df['N'] = df_current['value'] / (constants.e * revolution_freq)
	
	n = 2 * 2.68675E19 *  P_Torr / 760 

	integral_tmp = 2 / ( math.tan( theta_max / 2 )**2 )
	some_tmp = 1 / ( 4 * math.pi ) * ( z * Z * CONSTANTS.CGS.e / ( 2 * beta * CONSTANTS.CGS.c * p ) )

	df['derivation'] = -1 * CONSTANTS.CGS.c * beta * n * df['N'] 

	

# def coulumb_scattering_hours_wiedermann(p, eA, beta, P):
# 	"""
# 	Вычисляет время жизни пучка из-за рассеяния на остаточном газе.
	
# 	Параметры:
# 	P : давление газа [наноТорр]
# 	beta : значение бетатронной функции или скорость??? стр 321
# 	p : импульс пучка 
# 	theta_max : максимально допустимый угол рассеяния относительно движения частицы
# 	eA : acceptance of the beam transporl line? [mm mrad]
	
# 	Возвращает:
# 	tau : время жизни [часы]
# 	"""
# 	tmp1 = c * p # размерность должна быть ГэВ^2
# 	P = P * 10E9 # приводим к наноТорр
# 	tau = 10.25 * tmp1 / ( beta * P )
 
# 	return tau

# def coulumb_scattering_seconds_chao(beta, nZ, Z, A_perp, beta_perp, gamma):
# 	"""
# 	Вычисляет время жизни пучка из-за рассеяния на остаточном газе. стр 272 
	
# 	Параметры:
# 	beta : относительная скорость частицы
# 	nZ : количество атомов на одну молекулу газа
# 	p : импульс пучка 
# 	theta_max : максимально допустимый угол рассеяния относительно движения частицы
# 	eA : acceptance of the beam transporl line? [mm mrad]
	
# 	Возвращает:
# 	tau : время жизни [часы]
# 	"""
# 	ng = 9.656E24 * nZ
# 	re = 2.8179403267E-15
# 	sigma_el = 2 * math.pi * re**2 * Z**2 * beta_perp / ( gamma**2 * A_perp )
 
# 	tau = 1 / ( ng * beta * c * sigma_el )
	
# 	return tau
