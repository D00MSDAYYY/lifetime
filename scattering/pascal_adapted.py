from typing import Optional, Tuple, List
from datetime import datetime
import pandas as pd
import numpy as np

def pascal_scattering(df_current):
    # Инициализация переменных
    IBEAM: List[float] = []  # Инициализируем пустой список
    Km: int = 0
    CALI: float = 0.0
    DT: float = 1.0
    DI0: float = 50.0
    DELI0exp: float = 320.0
    Kmax: int = 210

    def __pascal_scattering(IBEAM_new: float):
        nonlocal Km, IBEAM  # Добавляем nonlocal для всех изменяемых переменных
        
        Km = Km + 1
        corrected_current = IBEAM_new - CALI

        if Km <= Kmax:
            # Расширяем массив если нужно
            if len(IBEAM) < Km:
                IBEAM.append(corrected_current)
            else:
                IBEAM[Km-1] = corrected_current  # Индексы с 0!
        else:
            # Сдвигаем массив
            IBEAM = IBEAM[1:] + [corrected_current]
            Km = Kmax

        S1 = S2 = S3 = 0
        TAU = None

        for K in range(1, Km):
            idx = Km - K - 1  # Корректный индекс
            if idx < 0:
                break
                
            CURR = IBEAM[idx]

            # Исправленное условие (было CURR < 500)
            if CURR > 500:  # Ток > 500 игнорируется
                break

            DELI = CURR - corrected_current
            if (DELI + DI0) > 0:
                S1 = S1 + K*K 
                S2 = S2 + CURR*K 
                S3 = S3 + CURR

            if (DELI - DELI0exp) > 0:
                break
            # Только если прошли все проверки
            SS = (K+1)/2 
            try:
                A = (S1 - K*SS*SS)/(S2 - S3*SS)
                TAU = DT * S3 / K * A

                if 0 < TAU and TAU <= 500000:
                    return TAU
            except (ZeroDivisionError, ValueError):
                continue
        return None  # Если не удалось вычислить

    # Создаем новый DataFrame для результатов
    results = []
    
    for index, row in df_current.iterrows():
        tau = __pascal_scattering(row["value"])

        if tau is not None:
            tau = tau / 3600
            results.append({
                'timestamp': row['timestamp'],
                'value': tau
            })

    df_result = pd.DataFrame(results)
    df_result['tag'] = 'pasc'

    return df_result