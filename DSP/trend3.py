import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error


def find_exp_trend(df):
	def exponential_decay(t, A, tau):
		"""
		Модель экспоненциального затухания
		y = A * exp(-t/tau) + C
		где:
		A - начальная амплитуда
		tau - постоянная времени (характерное время затухания)
		C - постоянное смещение (асимптота)
		"""
		return A * np.exp(-t / tau) 

	x_data = (current_df['timestamp'] - current_df['timestamp'].min()).dt.total_seconds()
	y_data = current_df['value'].values

	A0 = y_data[0] - y_data[-1] 
	tau0 = (x_data.iloc[-1] - x_data.iloc[0]) / 5 

	initial_guess = [A0, tau0]

	try:
		popt, pcov = curve_fit(exponential_decay, 
								x_data, y_data, 
								p0=initial_guess)
		
		A_fit, tau_fit = popt
		errors = np.sqrt(np.diag(pcov))

		y_pred = exponential_decay(x_data, *popt)

		r2 = r2_score(y_data, y_pred)
		rmse = np.sqrt(mean_squared_error(y_data, y_pred))

		print('parameters:', ' A = ', A_fit, ', tau = ', tau_fit)
		print('errors:', ' A_error = ', errors[0], ', tau_error = ', errors[1])
		print('metrics:', ' R2 = ', r2, ', RMSE = ', rmse)

		return y_pred, A_fit, tau_fit

	except Exception as e:
		print(f"Ошибка при подгонке: {e}")

def dft(df):
	time_data = df['timestamp']
	sampling_rate = 1 / (time_data.iloc[1] - time_data.iloc[0]).total_seconds()
	n = len(df)
	dft_result = np.fft.fft(df['value'])
	frequencies = np.fft.fftfreq(n, 1/sampling_rate)
	half_n = n // 2
	frequencies_half = frequencies[:half_n]

	magnitude = np.abs(dft_result[:half_n]) / n 

	return magnitude, frequencies_half


filename = '../data/beam/misc/2025-07-03.csv'

current_df = pd.read_csv(filename, 
				sep=';', 
				header=None, 
				names=['sensor_name', 'timestamp', 'value'])

current_df['timestamp'] = pd.to_datetime(current_df['timestamp'])
sensor_name = current_df['sensor_name'][0]

colors = [
    '#FF0000',  # ярко-красный
    '#0000FF',  # ярко-синий  
    '#00FF00',  # ярко-зеленый
    '#FFA500',  # оранжевый
    '#800080',  # фиолетовый
    '#FF00FF',  # маджента
    '#00FFFF',  # циан
    '#FFFF00',  # желтый
    '#FF4500',  # красно-оранжевый
    '#008000',  # темно-зеленый
    '#000080',  # темно-синий
    '#800000',  # темно-красный
    '#808000',  # оливковый
    '#008080',  # бирюзовый
    '#800080',  # пурпурный
    '#FF1493',  # глубокий розовый
    '#00FF7F',  # весенне-зеленый
    '#FFD700',  # золотой
    '#DC143C',  # малиновый
    '#4682B4'   # стальной синий
]

parts = np.array_split(current_df, 20)

# date_tau_list = []

frankeshtein_df = None

for i, part in enumerate(parts): 
	part_df = pd.DataFrame(part)
	part_df['value'] = part_df['value'].astype(float)
	part_df['value'] = part_df['value'].rolling(window=2, center=True, min_periods=1).mean()

	y_predicted, A_fit, tau_fit = find_exp_trend(part_df)

	y_df = part_df.copy()
	y_df['value'] = y_predicted

	plt.figure(figsize=(12, 8))
	plt.xlabel('Время')
	plt.ylabel('Значение')
	plt.title(f'Экспоненциальная подгонка: {sensor_name}\n'
			f'y = {A_fit:.3f} * exp(-t/{tau_fit:.3f})')
	plt.grid(True, alpha=0.3)
	plt.xticks(rotation=45)
	plt.tight_layout()
	plt.plot(part_df['timestamp'], part_df['value'], 'bo-', 
				alpha=0.7, label='Исходные данные', markersize=4)
	plt.plot(y_df['timestamp'], y_df['value'], 'r-', 
				linewidth=2, label='Экспоненциальная модель')
	plt.legend()

	# avg_date = pd.Series([current_df['timestamp'].iloc[0], current_df['timestamp'].iloc[-1]]).mean()
	# date_tau_list.append([avg_date, tau_fit])

	if frankeshtein_df is None:
		frankeshtein_df = y_df
	else:
		frankeshtein_df = pd.concat([frankeshtein_df, y_df])

	# untrended_df = part_df.copy()
	# untrended_df['value'] = part_df['value'] - y_predicted
	# untrended_df['value'] = untrended_df['value'] - untrended_df['value'].mean()

	# plt.figure(figsize=(12, 8))
	# plt.plot(untrended_df['timestamp'], untrended_df['value'], 'bo-', 
	# 			alpha=0.7, label='Вычтенный тренд', markersize=4)
	# plt.legend()
	# plt.xlabel('Время')
	# plt.ylabel('Значение')
	# plt.title(f'Вычтенный тренд')
	# plt.grid(True, alpha=0.3)
	# plt.xticks(rotation=45)
	# plt.tight_layout()

	# magnitude, frequencies_half = dft(untrended_df)
	# magnitude_filtered = pd.Series(magnitude).rolling(window=7, center=True, min_periods=1).mean()

	# magnitude_db = 20 * np.log10(magnitude)  
	# magnitude_filtered_db = 20 * np.log10(magnitude_filtered)  

	# color = colors[i % len(colors)]

	# plt.plot(frequencies_half, magnitude_db, color=color, linewidth=1, alpha=0.4, label='Исходная')
	# plt.plot(frequencies_half, magnitude_filtered_db, color="grey", linewidth=1, alpha=0.5, label='Сглаженная')
	# plt.legend()
	# plt.xlabel('Частота (Гц)')
	# plt.ylabel('Амплитуда (дБ)')
	# plt.title('Амплитудный спектр')
	# plt.grid(True, alpha=0.3)
	# plt.xlim(0, min(1, frequencies_half[-1]))


# date_tau_df = pd.DataFrame(date_tau_list, columns=['timestamp', 'value'])
# date_tau_df['value'] = date_tau_df['value'] / 3600

# plt.figure(figsize=(12, 8))
# plt.plot(date_tau_df['timestamp'], date_tau_df['value'], 'bo-', 
# 			alpha=0.7, label='Тау от времени', markersize=4)
# plt.legend()
# plt.xlabel('Время')
# plt.ylabel('Значение')
# plt.title(f'Вычтенный тренд')
# plt.grid(True, alpha=0.3)
# plt.xticks(rotation=45)
# plt.tight_layout()

plt.figure(figsize=(12, 8))
plt.plot(current_df['timestamp'], current_df['value'], 'g-', 
			alpha=0.7, label='исходная', markersize=4)
plt.plot(frankeshtein_df['timestamp'], frankeshtein_df['value'], 'r-', 
			alpha=0.7, label='frankeshtein', markersize=4)
plt.legend()
plt.xlabel('Время')
plt.ylabel('Значение')
plt.title(f'Вычтенный тренд')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()