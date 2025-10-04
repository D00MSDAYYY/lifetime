import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error

filename = '../data/beam/misc/2025-06-30.csv'
sensor_name = 'current sensor'

current_df = pd.read_csv(filename, 
				sep=';', 
				header=None, 
				names=['sensor_name', 'timestamp', 'value'])

# Преобразуем timestamp в datetime
current_df['timestamp'] = pd.to_datetime(current_df['timestamp'])

# Преобразуем значение в float
current_df['value'] = current_df['value'].astype(float)

plt.figure(figsize=(12, 6))

plt.plot(current_df['timestamp'], current_df['value'], 
			linewidth=1, marker='o', markersize=2, label='Данные датчика')

# Настройка внешнего вида графика
plt.xlabel('Время')
plt.ylabel('Значение')

if sensor_name:
	plt.title(f'Данные датчика: {sensor_name}')
else:
	plt.title('Данные датчика')

plt.grid(True, alpha=0.3)
plt.legend()

plt.xticks(rotation=45)
plt.tight_layout()

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
	# Нелинейная подгонка
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
	if sensor_name:
		plt.title(f'Данные датчика: {sensor_name}')
	else:
		plt.title('Данные датчика')
	plt.grid(True, alpha=0.3)
	plt.legend()
	plt.xticks(rotation=45)
	plt.tight_layout()

	# Исходные данные
	plt.plot(current_df['timestamp'], current_df['value'], 'bo-', 
				alpha=0.7, label='Исходные данные', markersize=4)

	# Подобранная кривая
	plt.plot(current_df['timestamp'], y_pred, 'r-', 
				linewidth=2, label='Экспоненциальная модель')
	
	plt.show()

	print('parameters:', ' A = ', A_fit, ', tau = ', tau_fit, ', C = ', C_fit)
	print('errors:', ' A_error = ', errors[0], ', tau_error = ', errors[1], ', C_error = ', errors[2])
	print('metrics:', ' R2 = ', r2, ', RMSE = ', rmse)
	print('predictions: ', y_pred)
	print('time_numeric: ', x_data)

except Exception as e:
	print(f"Ошибка при подгонке: {e}")