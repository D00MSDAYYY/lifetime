import math
from scipy import constants

def bremsstahlung_scattering_wiedemann(P_Torr, energy_acceptance):
	"""
	
	particle_accelerator_physics_3ed_wiedemann.pdf стр 328
	
	Возвращает:
	tau : время жизни [часы]
	"""
	P_nTorr = P_Torr / 1e-9

	tau_inv = 0.00653 * P_nTorr * math.log(1 / energy_acceptance)

	tau = 1 / tau_inv

	return tau


def bremstahlung_scattering_chao(beta, nZ,  A, X0, dp_p_lim_acceptance, P_Torr, T_K):
	"""
	
	handbook_of_accelerator_physics_and_engineering_2ed_chao.pdf стр 272
	
	Возвращает:
	tau : время жизни [часы]
	"""

	ng = 9.656E24 * nZ * P_Torr / T_K
	
	sigma_br = (4 / 3) * ( A / constants.Avogadro ) * ( 1 / X0 ) * ( math.log( 1 / dp_p_lim_acceptance) - 5 / 8 )

	tau = 1 / (ng * beta * constants.c * sigma_br)

	return tau
