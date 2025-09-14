from scipy import constants
import math

def _aux_e_m(delta_m, beta_x, sigma_x, gamma, sigma_x_beta, avg_sigma_x):
	upper = delta_m**3 * beta_x**2 * sigma_x**2
	bottom = gamma**2 * sigma_x_beta**2 * avg_sigma_x**2
	result = upper / bottom
	return result


def touschek_scattering_wiedemann(N, r_0, beta_x, e_x, beta, gamma, sigma_p, Phi_x, sigma_x, sigma_y, sigma_z, e_m ):
	first = ( N * r_0 * constants.c ) / ( 8 * math.pi * beta * gamma * sigma_z )
	C_e_m = 99999999
	second = ( ( ( beta_x / e_x )**( 3 / 2 ) * C_e_m ) / ( 1 + ( ( sigma_p * beta_x * Phi_x ) / sigma_x )**2 )**( 3 / 2 ) * sigma_x * sigma_y * e_m )



	