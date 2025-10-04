import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error

filename = '../data/beam/misc/2025-06-30.csv'

current_df = pd.read_csv(filename, 
				sep=';', 
				header=None, 
				names=['sensor_name', 'timestamp', 'value'])

# Преобразуем timestamp в datetime
current_df['timestamp'] = pd.to_datetime(current_df['timestamp'])
sensor_name = current_df['sensor_name'][0]

current_df['value'] = current_df['value'].astype(float)

# фильтрую скользящим средним
current_df['value'] = current_df['value'].rolling(window=7, center=True, min_periods=1).mean()

# plt.figure(figsize=(12, 6))
# plt.plot(current_df['timestamp'], current_df['value'], 
# 			linewidth=1, marker='o', markersize=2, label='Данные датчика')
# plt.xlabel('Время')
# plt.ylabel('Значение')

# plt.title(f'Отфильтрованные данныe: {sensor_name}')
# plt.grid(True, alpha=0.3)
# plt.xticks(rotation=45)
# plt.tight_layout()

def exponential_decay(t, A, tau, C):
    """
    Модель экспоненциального затухания
    y = A * exp(-t/tau) + C
    где:
    A - начальная амплитуда
    tau - постоянная времени (характерное время затухания)
    C - постоянное смещение (асимптота)
    """
    return A * np.exp(-t / tau) + C

x_data = (current_df['timestamp'] - current_df['timestamp'].min()).dt.total_seconds()
y_data = current_df['value'].values

# Начальное приближение для параметров
A0 = y_data[0] - y_data[-1]  # начальная амплитуда
tau0 = (x_data.iloc[-1] - x_data.iloc[0]) / 5  # начальная оценка tau
C0 = y_data[-1]  # асимптотическое значение

initial_guess = [A0, tau0, C0]

try:
	popt, pcov = curve_fit(exponential_decay, 
							x_data, y_data, 
							p0=initial_guess)
	
	A_fit, tau_fit, C_fit = popt
	errors = np.sqrt(np.diag(pcov))  # стандартные ошибки параметров
	
	# Расчет предсказанных значений
	y_pred = exponential_decay(x_data, *popt)
	
	# Метрики качества
	r2 = r2_score(y_data, y_pred)
	rmse = np.sqrt(mean_squared_error(y_data, y_pred))
	
	plt.figure(figsize=(12, 8))
	plt.xlabel('Время')
	plt.ylabel('Значение')
	plt.title(f'Экспоненциальная подгонка: {sensor_name}\n'
              f'y = {A_fit:.3f} * exp(-t/{tau_fit:.3f}) + {C_fit:.3f}')
	plt.grid(True, alpha=0.3)
	plt.xticks(rotation=45)
	plt.tight_layout()

	# Исходные данные
	plt.plot(current_df['timestamp'], current_df['value'], 'bo-', 
				alpha=0.7, label='Исходные данные', markersize=4)

	# Подобранная кривая
	plt.plot(current_df['timestamp'], y_pred, 'r-', 
				linewidth=2, label='Экспоненциальная модель')

	print('parameters:', ' A = ', A_fit, ', tau = ', tau_fit, ', C = ', C_fit)
	print('errors:', ' A_error = ', errors[0], ', tau_error = ', errors[1], ', C_error = ', errors[2])
	print('metrics:', ' R2 = ', r2, ', RMSE = ', rmse)

except Exception as e:
	print(f"Ошибка при подгонке: {e}")

untrended_values = current_df['value'] - y_pred

plt.figure(figsize=(12, 8))
plt.plot(current_df['timestamp'], untrended_values, 'bo-', 
			alpha=0.7, label='Вычтенный тренд', markersize=4)
plt.xlabel('Время')
plt.ylabel('Значение')
plt.title(f'Вычтенный тренд')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

time_data = current_df['timestamp']
sampling_rate = 1 / (time_data[1] - time_data[0]).total_seconds()
n = len(untrended_values)
dft_result = np.fft.fft(untrended_values)
frequencies = np.fft.fftfreq(n, 1/sampling_rate)

# Берем первую половину (симметричный спектр)
half_n = n // 2
frequencies_half = frequencies[:half_n]
magnitude = np.abs(dft_result[:half_n]) / n

magnitude_filtered = magnitude
magnitude_filtered_db = 20 * np.log10(magnitude_filtered + 1e-10)  # В дБ для лучшей видимости
magnitude_db = 20 * np.log10(magnitude + 1e-10)  

plt.figure(figsize=(12, 8))
plt.plot(frequencies_half, magnitude_db, 'm-', linewidth=1, alpha=0.7)
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда (дБ)')
plt.title('Амплитудный спектр (DFT) - Логарифмическая шкала')
plt.grid(True, alpha=0.3)
plt.xlim(0, min(1, frequencies_half[-1]))

plt.show()