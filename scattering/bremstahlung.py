import math
from scipy import constants

def bremstahlung_scattering_chao(beta, nZ,  A, X0, dp_p_lim_acceptance):
	ng = 9.656E24 * nZ
	
	sigma_br = (4 / 3) * ( A / constants.Avogadro ) * ( 1 / X0 ) * ( math.log( 1 / dp_p_lim_acceptance) - 5 / 8 )

	tau = 1 / (ng * beta * constants.c * sigma_br)

	return tau
