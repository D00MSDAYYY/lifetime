import math
from scipy import constants

gases = {
    "N2": {
        "fraction": 1.0,    # Доля в смеси (0% - можно изменить при необходимости)
        "mass": 28.0134,    # Молекулярная масса [г/моль]
        "Z": 7,             # Атомный номер азота (Z=7)
        "n_Z": 2            # 2 атома N в молекуле N₂
    }
}

Z_avg = sum(gas["fraction"] * gas["Z"] for gas in gases.values())
n_Z_avg = sum(gas["fraction"] * gas["n_Z"] for gas in gases.values())
A_avg = sum(gas["fraction"] * gas["mass"] for gas in gases.values())

T_gas_K = 293 # температура газа в К
r_0 = 2.817e-15 # классический радиус электрона

# система CGS
class _aux_CGS:
	pass
CGS = _aux_CGS()

CGS.e = 4.803e-10			# Элементарный заряд [см³/²·г¹/²·с⁻¹] (статикулон)
CGS.e_mass = 9.1094E-28 	# граммы
CGS.c = 2.998e10			# Скорость света [см/с]

# данные об ускорителе Сибирь-2
class _aux_Siberia2:
	pass
siberia2 = _aux_Siberia2()

siberia2.beta = 1
siberia2.AverageBetatronXFunction = 10
siberia2.AverageBetatronYFunction = 5
siberia2.AverageBetatronFunction = ( siberia2.AverageBetatronXFunction + siberia2.AverageBetatronYFunction ) / 2
siberia2.HorizontalAperture = 20e-3 
siberia2.VerticalAperture = 12e-3 
siberia2.eA = 10e-3**2 / siberia2.AverageBetatronFunction 
siberia2.eA_mm_mrad = 10 # check this
siberia2.P_Pa = 1E-7
siberia2.P_Torr = siberia2.P_Pa * ( 7.50062 * 1E-3 )
siberia2.RevolutionFrequency = 2.4147E6
siberia2.Energy_GeV = 2.5
siberia2.gamma = siberia2.Energy_GeV / 0.511e-3


