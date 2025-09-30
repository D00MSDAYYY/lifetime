import math
import CONSTANTS_CONFIG
import numpy as np
from scipy import constants

def elastic_scattering_wiedemann(beta, P_Torr, z, Z, p, theta_max):
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
	# print("beta", beta)
	# print("P_Torr",P_Torr)
	# print("z",z)
	# print("Z",Z)
	# print("p", p)
	# print("theta_max",theta_max)
	# print("CONSTANTS_CONFIG.CGS.c",CONSTANTS_CONFIG.CGS.c)

	paren = (z * Z * CONSTANTS_CONFIG.CGS.e**2 / (2 * beta  * CONSTANTS_CONFIG.CGS.c * p))**2

	tau_inv = CONSTANTS_CONFIG.CGS.c * beta * 2 * constants.Avogadro * P_Torr / 760 * ( paren ) * 4 * math.pi / (math.tan(theta_max / 2)**2)
	
	tau = 1 / tau_inv

	tau_hours = tau  / 3600

	return tau_hours

def elastic_scattering_wiedemann2(p_CGS, eA, b_m, P_nTorr):
	"""
	Вычисляет время жизни пучка из-за рассеяния на остаточном газе в системе CGS.

	particle_accelerator_physics_3ed_wiedemann.pdf стр 323

	Возвращает:
	tau_hours : время жизни [часы]
	"""

	# print("p_CGS", p_CGS)
	# print("eA", eA)
	# print("b_m", b_m)
	# print("P_nTorr", P_nTorr)

	tau_hours = 10.25 * ( p_CGS**2 * eA ) / ( b_m * P_nTorr )

	return tau_hours

def elastic_scattering_chao(beta, nZ, Z, A_acceptance, beta_func_value, gamma, P_Torr, T_K):
	"""

	handbook_of_accelerator_physics_and_engineering_2ed_chao.pdf стр 272
	
	Возвращает:
	tau : время жизни [часы]
	"""
	print("beta",beta)
	print("nZ",nZ)
	print("Z",Z)
	print("A_acceptance",A_acceptance)
	print("beta_func_value",beta_func_value)
	print("gamma",gamma)
	print("P_Torr",P_Torr)
	print("T_K",T_K)

	ng = 9.656E24 * nZ * P_Torr / T_K

	r_e, _, _ = constants.physical_constants['classical electron radius']

	sigma_el = 2 * math.pi * r_e**2 * Z**2 * beta_func_value / ( gamma**2 * A_acceptance )

	inv = ng * beta * constants.c * sigma_el

	tau = 1 / inv / 3600

	return tau
