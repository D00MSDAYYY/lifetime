import math
from scipy import constants

gases = {
	"H2": {
		"fraction": 0.7,    # Доля в смеси (70%)
		"mass": 2.016,      # Молекулярная масса [г/моль]
		"Z": 1,             # Атомный номер (для водорода Z=1)
		"n_Z": 2            # 2 атома H в молекуле H₂
	},
	"CO": {
		"fraction": 0.2,    # Доля в смеси (20%)
		"mass": 28.010,     # Молекулярная масса [г/моль]
		"Z": 7,             # Средний атомный номер (C=6 + O=8 → 7)
		"n_Z": 2            # 2 атома (1C + 1O)
	},
	"H2O": {
		"fraction": 0.1,    # Доля в смеси (10%)
		"mass": 18.015,     # Молекулярная масса [г/моль]
		"Z": 3.33,          # Средний атомный номер (2H + O → (2*1 + 8)/3 ≈ 3.33)
		"n_Z": 3            # 3 атома (2H + 1O)
	}
}

z = constants.e
Z_eff = math.sqrt(sum(gas["fraction"] * gas["Z"]**2 for gas in gases.values()))
Z_avg = sum(gas["fraction"] * gas["Z"] for gas in gases.values())
A_avg = sum(gas["fraction"] * gas["mass"] for gas in gases.values())


# система CGS
class _aux_CGS:
    pass
CGS = _aux_CGS()

CGS.e = 4.803e-10 # Элементарный заряд [см³/²·г¹/²·с⁻¹] (статикулон)
CGS.e_mass = 9.1094E-28 # граммы
CGS.c = 2.998e10          # Скорость света [см/с]


# данные об ускорителе Сибирь-2
class _aux_Siberia2:
    pass
siberia2 = _aux_Siberia2()

siberia2.beta = 1
siberia2.AverageBetatronXFunction = 10
siberia2.AverageBetatronYFunction = 5
siberia2.AverageBetatronFunction = ( siberia2.AverageBetatronXFunction + siberia2.AverageBetatronYFunction ) / 2
siberia2.eA = 50 # beam chamber radius
siberia2.P_Pa = 1E-7
siberia2.P_Torr = siberia2.P_Pa * ( 7.50062 * 1E-3 )
siberia2.RevolutionFrequency = 2.4147E6
siberia2.Energy_GeV = 2.3
siberia2.gamma = siberia2.Energy_GeV / 0.000511


