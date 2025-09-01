import math
import CONFIG

from scipy import constants

def coulomb_scattering_wiedermann(beta, P_Torr, z, Z, p, theta_max):
	"""
	Вычисляет время жизни пучка из-за рассеяния на остаточном газе в системе CGS.

	particle_accelerator_physics_3ed_wiedemann.pdf стр 323
	
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

	tau_inv = CONFIG.CGS.c * beta * 2 * constants.Avogadro * P_Torr / 760 * ( paren ) * 4 * math.pi / (math.tan(theta_max / 2)**2)
	
	tau = 1 / tau_inv

	tau_hours = tau  # Перевод в часы ?

	return tau_hours

def coulomb_scattering_chao(beta, nZ, Z, A_acceptance, beta_func_value, gamma, P_Torr, T_K):
	"""

	handbook_of_accelerator_physics_and_engineering_2ed_chao.pdf стр 272
	
	Возвращает:
	tau : время жизни [часы]
	"""
	ng = 9.656E24 * nZ * P_Torr / T_K

	re, _, _ = constants.physical_constants['classical electron radius']

	sigma_el = 2 * math.pi * re**2 * Z**2 * beta_func_value / ( gamma**2 * A_acceptance )

	tau = 1 / (ng * beta * constants.c * sigma_el) 

	return tau


