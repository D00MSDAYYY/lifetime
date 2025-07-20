import math

c = 3e8  # скорость света [м/с]
e = 1.6e-19  # элементарный заряд [Кл]
NA = 6.02214076e23  # число Авогадро [частиц/моль]

def coulumb_scattering_seconds_wiedermann(P, z, Z, beta, p, theta_max):
	"""
	Вычисляет время жизни пучка из-за рассеяния на остаточном газе.
	
	Параметры:
	P : давление газа [Торр]
	z : заряд ускоряемой частицы
	Z : заряд ядра атома газа
	beta : значение бетатронной функции или скорость??? стр 321 [m]
	p : импульс пучка 
	theta_max : максимальный угол рассеяния [радианы]

	Возвращает:
	tau : время жизни [секунды]
	"""
	tmp1 = c * beta * 2 * NA
	tmp2 = P / 760
	tmp3 = ( z * Z * e**2 / ( 2 * beta * c * p ) )**2
	tmp4 = 4 * math.pi / ( math.tan(theta_max / 2 ) )**2
 
	tau = tmp1 * tmp2 * tmp3 * tmp4
 
	return tau

def coulumb_scattering_hours_wiedermann(p, eA, beta, P):
	"""
	Вычисляет время жизни пучка из-за рассеяния на остаточном газе.
	
	Параметры:
	P : давление газа [наноТорр]
	beta : значение бетатронной функции или скорость??? стр 321
	p : импульс пучка 
	theta_max : максимально допустимый угол рассеяния относительно движения частицы
	eA : acceptance of the beam transporl line? [mm mrad]
	
	Возвращает:
	tau : время жизни [часы]
	"""
	tmp1 = c * p # размерность должна быть ГэВ^2
	P = P * 10E9 # приводим к наноТорр
	tau = 10.25 * tmp1 / ( beta * P )
 
	return tau

def coulumb_scattering_seconds_chao(beta, nZ, Z, A_perp, beta_perp, gamma):
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
	re = 2.8179403267E-15
	sigma_el = 2 * math.pi * re**2 * Z**2 * beta_perp / ( gamma**2 * A_perp )
 
	tau = 1 / ( ng * beta * c * sigma_el )
	
	return tau
