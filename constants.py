# система CGS
class _aux_CGS:
    pass
CGS = _aux_CGS()

CGS.e = 4.803e-10 # Элементарный заряд [см³/²·г¹/²·с⁻¹] (статикулон)
CGS.c = 2.998e10          # Скорость света [см/с]



# данные об ускорителе Сибирь-2
class _aux_Siberia2:
    pass
siberia2 = _aux_Siberia2()

# siberia2.StaticAperture = 
# siberia2.DynamicAperture = 
siberia2.AverageBetatronXFunction = 10
siberia2.AverageBetatronYFunction = 5
siberia2.AverageBetatronFunction = ( siberia2.AverageBetatronXFunction + siberia2.AverageBetatronYFunction ) / 2
siberia2.eA = 50 # beam chamber radius
siberia2.P_Pa = 1E-7
siberia2.P_Torr = siberia2.P_Pa * ( 7.50062 * 1E-3 )
siberia2.RevolutionFrequency = 2.4147E6
siberia2.Energy_GeV = 2.3


