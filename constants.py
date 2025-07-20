
# физические константы ( надо будет заменить на константы из scipy)

e = 1.6e-19  # элементарный заряд [Кл]
c = 3e8  # скорость света [м/с]
NAvogadro = 6.02214076e23  # число Авогадро [частиц/моль]

# данные об ускорителе Сибирь-2
class _aux_Siberia2:
    pass
siberia2 = _aux_Siberia2()

# siberia2.StaticAperture = 3
# siberia2.DynamicAperture = 3
siberia2.AverageBetatronXFunction = 10
siberia2.AverageBetatronYFunction = 5
siberia2.AverageBetatronFunction = ( siberia2.AverageBetatronXFunction + siberia2.AverageBetatronYFunction ) / 2
siberia2.eA = 50
siberia2.P_Pa = 1E-7
siberia2.P_Torr = siberia2.P_Pa * ( 7.50062 * 1E-3 )


