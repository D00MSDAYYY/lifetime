
IBEAM new - измеренный ток пучка в мкА, double, 
ITIMEnew - время измерения, DateTime, 
CALI - вычитаемый фон, результат калибровки измерений, 
DT - период измерений тока в сек, double, (по умолчанию 1), 
DI0 - допустимый спад тока в мкА, double, (по умолчанию 50), 
DELI0inj - допустимый суммарный спад тока на инжекции в мкА, double, (по умолчанию 160), 
DELI0exp - допустимый суммарный спад тока на полной энергии в мкА, double, (по умолчанию 320), 
IBEAM[1…Kmax] - массив измерений тока в мкА, array of double, 
Kmax - максимально допустимое количество измерений, int, (по умолчанию 210), 
Km - номер измерения, int, 
S1, S2, S3 - вспомогательные интегралы, double, 
TAU - вычисленное время жизни в сек, double, 

Km := 0 
Km := Km + 1 
If (Km <= Kmax) then
	IBEAM [Km] := IBEAMnew - CALI 
Else 
	begin 
	IBEAM [Kmax] := IBEAMnew 
	Km := Kmax 
	end 
	S1 := S2 := S3 := 0 
	From K=1 to Km-1 do 
	Begin 
	CURR := IBEAM[Km-K] 
	If (CURR>500) then (цикл прекращается, вр. Жизни не вычисляется и не записывается в БД) 
	DELI := CURR - IBEAMnew 
	If (DELI + DI0) > 0 then goto label3 
	If(K<=1) then (цикл прекращается, вр. Жизни не вычисляется и не записывается в БД) 
	Else goto label1 
label3 
S1 := S1 + K*K 
S2 := S2 + CURR*K 
S3 := S3 + CURR 

If(DELI - DELI0exp)>0 then goto label1 \\аналогично для режима инжекции 
End 

label1 If(K<2) then (цикл прекращается, вр. Жизни не вычисляется и не записывается в БД) 
(текст, который нужно закомментировать) 
label1 If(K<1) then (цикл прекращается, вр. Жизни не вычисляется и не записывается в БД) 
	If(K>1) then goto label4 
	TAU:=CURR/DELI*DT 
goto label 5 
label4 SS := (K+1)/2 
A:=(S1-K*SS*SS)/(S2-S3*SS) 
TAU := DT*S3/K*A 
	If(TAU<0) or (TAU>500000) then (вр. Жизни и не записывается в БД) 

