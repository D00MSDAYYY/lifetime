import math
import CONFIG

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
	paren = (z * Z * CONFIG.CGS.e**2 / (2 * beta * CONFIG.CGS.c * p))**2
	tau_inv = 2 * CONFIG.CGS.c * beta * constants.Avogadro * P_Torr / 760 * ( paren ) * 4 * math.pi / (math.tan(theta_max / 2)**2)
	tau = 1 / tau_inv

	tau_hours = tau / 3600  # Перевод в часы

	return tau_hours

def coulomb_scattering_zaycev(df_current, revolution_freq, beta, P_Torr, z, Z, p, theta_max):
	"""
	Вычисляет время жизни пучка в каждой точке на основе производной.
	
	Параметры:
	df_current : DataFrame с колонкой 'value' (ток пучка [A])
	revolution_freq : частота обращения частиц [Гц]
	beta : v/c частиц
	P_Torr : давление газа [Торр]
	z, Z : заряды частицы и ядра газа
	p : импульс [г·см/с] (CGS)
	theta_max : максимальный угол рассеяния [рад]
	
	Возвращает:
	df : DataFrame с колонками 'N', 'derivation', 'tau'
	"""
	df = df_current.copy()
	df['tag'] = 'coulomb_zaycev'
	
	# Число частиц
	df['N'] = df_current['value'] / (constants.e * revolution_freq)
	
	# Плотность газа [см^-3] (CGS)
	n = 2 * 2.68675e19 * P_Torr / 760  # 2.68675e19 — число Лошмидта
	
	# Вычисление производной dN/dt
	integral_tmp = 2 / ( math.tan( theta_max / 2 )**2 )
	some_tmp = 1 / ( 4 * math.pi * constants.epsilon_0 ) * ( z * Z * CONFIG.CGS.e / ( 2 * beta * CONFIG.CGS.c * p ) )
	
	df['derivation'] = -1 * 2 * math.pi * CONFIG.CGS.c * beta * n * df['N'] * (4 * math.pi * some_tmp * integral_tmp)

	# Время жизни tau = -N / (dN/dt)
	df['value'] = -df['N'] / df['derivation'] / 3600

	return df


def coulomb_scattering_chao(beta, nZ, Z, A_acceptance, beta_func_value, gamma):
	"""
	Вычисляет время жизни пучка из-за рассеяния на остаточном газе. стр 272 
	
	Параметры:
	beta : относительная скорость частицы
	nZ : количество атомов на одну молекулу газа
	p : импульс пучка 
	theta_max : максимально допустимый угол рассеяния относительно движения частицы
	eA : acceptance of the beam transporl line? [mm mrad]
	
	Возвращает:
	tau : время жизни [часы]
	"""
	ng = 9.656E24 * nZ
	re, _, _ = constants.physical_constants['classical electron radius']

	sigma_el = 2 * math.pi * re**2 * Z**2 * beta_func_value / ( gamma**2 * A_acceptance )
	tau = 1 / (ng * beta * constants.c * sigma_el) / 3600

	return tau


