import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error


def find_exp_trend(df):
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

	A0 = y_data[0] - y_data[-1] 
	tau0 = (x_data.iloc[-1] - x_data.iloc[0]) / 5 
	C0 = y_data[-1]

	initial_guess = [A0, tau0, C0]

	try:
		popt, pcov = curve_fit(exponential_decay, 
								x_data, y_data, 
								p0=initial_guess)
		
		A_fit, tau_fit, C_fit = popt
		errors = np.sqrt(np.diag(pcov))

		y_pred = exponential_decay(x_data, *popt)

		r2 = r2_score(y_data, y_pred)
		rmse = np.sqrt(mean_squared_error(y_data, y_pred))

		print('parameters:', ' A = ', A_fit, ', tau = ', tau_fit, ', C = ', C_fit)
		print('errors:', ' A_error = ', errors[0], ', tau_error = ', errors[1], ', C_error = ', errors[2])
		print('metrics:', ' R2 = ', r2, ', RMSE = ', rmse)

		return y_pred, A_fit, tau_fit, C_fit

	except Exception as e:
		print(f"Ошибка при подгонке: {e}")

def dft(df):
	time_data = df['timestamp']
	sampling_rate = 1 / (time_data[1] - time_data[0]).total_seconds()
	n = len(df)
	dft_result = np.fft.fft(df['value'])
	frequencies = np.fft.fftfreq(n, 1/sampling_rate)
	half_n = n // 2
	frequencies_half = frequencies[:half_n]

	magnitude = np.abs(dft_result[:half_n]) / n 

	return magnitude, frequencies_half


filename = '../data/beam/misc/2025-06-30.csv'

current_df = pd.read_csv(filename, 
				sep=';', 
				header=None, 
				names=['sensor_name', 'timestamp', 'value'])

current_df['timestamp'] = pd.to_datetime(current_df['timestamp'])
sensor_name = current_df['sensor_name'][0]

current_df['value'] = current_df['value'].astype(float)
current_df['value'] = current_df['value'].rolling(window=31, center=True, min_periods=1).mean()

y_predicted, A_fit, tau_fit, C_fit = find_exp_trend(current_df)

plt.figure(figsize=(12, 8))
plt.xlabel('Время')
plt.ylabel('Значение')
plt.title(f'Экспоненциальная подгонка: {sensor_name}\n'
		f'y = {A_fit:.3f} * exp(-t/{tau_fit:.3f}) + {C_fit:.3f}')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.plot(current_df['timestamp'], current_df['value'], 'bo-', 
			alpha=0.7, label='Исходные данные', markersize=4)
plt.plot(current_df['timestamp'], y_predicted, 'r-', 
			linewidth=2, label='Экспоненциальная модель')
plt.legend()

untrended_df = current_df.copy()
untrended_df['value'] = current_df['value'] - y_predicted
untrended_df['value'] = untrended_df['value'] - untrended_df['value'].mean()

plt.figure(figsize=(12, 8))
plt.plot(untrended_df['timestamp'], untrended_df['value'], 'bo-', 
			alpha=0.7, label='Вычтенный тренд', markersize=4)
plt.legend()
plt.xlabel('Время')
plt.ylabel('Значение')
plt.title(f'Вычтенный тренд')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

magnitude, frequencies_half = dft(untrended_df)
magnitude_filtered = pd.Series(magnitude).rolling(window=7, center=True, min_periods=1).mean()

magnitude_db = 20 * np.log10(magnitude)  
magnitude_filtered_db = 20 * np.log10(magnitude_filtered)  

plt.figure(figsize=(12, 8))
plt.plot(frequencies_half, magnitude_db, 'm-', linewidth=1, alpha=0.4, label='Исходная')
plt.plot(frequencies_half, magnitude_filtered_db, 'g-', linewidth=1, alpha=0.8, label='Сглаженная')
plt.legend()
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда (дБ)')
plt.title('Амплитудный спектр')
plt.grid(True, alpha=0.3)
plt.xlim(0, min(1, frequencies_half[-1]))

plt.show()