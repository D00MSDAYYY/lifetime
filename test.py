import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from scipy.signal import savgol_filter
from pykalman import KalmanFilter


# Физические константы
e = 1.6e-19  # элементарный заряд [Кл]

def calculate_lifetime(df, revolution_freq=3.1e6):
	"""
	Расчет времени жизни пучка через экспоненциальный распад
	с учетом миллисекундного разрешения временных меток
	
	Параметры:
	df - DataFrame с данными о токе
	revolution_freq - частота обращения частиц [Гц]
	
	Возвращает:
	Series с временем жизни в часах
	"""
	# Конвертируем ток в число частиц
	df['N'] = df['value'] / (e * revolution_freq)
	
	# Вычисляем разницу между текущим и предыдущим значением
	df['delta_t'] = df['timestamp'].diff().dt.total_seconds()
	
	# Расчет tau по формуле: N_curr = N_0 * exp(-Δt/τ)
	with np.errstate(divide='ignore', invalid='ignore'):
		df['tau'] = -df['delta_t'] / np.log(df['N'] / df['N'].shift(1))
	
	# Переводим секунды в часы и убираем выбросы
	df['lifetime'] = df['tau'] / 3600
	df['lifetime'] = df['lifetime'].where(df['lifetime'].between(0, 1000))  # Фильтр нереальных значений
	
	return df['lifetime']

def plot(file_list, output_image=None, output_csv=None):
	"""
	Построение графиков тока и времени жизни пучка с миллисекундным разрешением
	"""
	try:
		fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12), sharex=True)
		
		for file_path in file_list:
			# Чтение данных с учетом формата
			df = pd.read_csv(
				file_path, 
				sep=';', 
				header=None,
				usecols=[0, 1, 2],
				names=['tag', 'timestamp', 'value'],
				engine='python',
				na_values=[''],
				skipinitialspace=True
			)
			
			# Преобразование timestamp в datetime с миллисекундной точностью
			df['timestamp'] = pd.to_datetime(
				df['timestamp'].str.strip(),  # Удаление пробелов для строк
				format='%Y-%m-%d %H:%M:%S.%f',
				errors='coerce'
			)
			
			# Преобразование значения тока в числовой формат
			df['value'] = pd.to_numeric(
				df['value'].astype(str).str.strip().str.replace(',', '.'),
				errors='coerce'
			)
			
			# Удаление строк с NaN значениями
			df.dropna(subset=['timestamp', 'value'], inplace=True)
			
			# Сглаживание данных
			window_size = min(
				31,  # Максимальный размер окна
				max(
					3,  # Минимальный размер окна
					len(df) // 1000  # 1 точка на 1000 строк
				)
			)
			df['value'] = df['value'].rolling(
			window=window_size, 
			center=True, 
			min_periods=1
			).mean()

			# df['value'] = savgol_filter( 
			# 	df['value'],
			# 	window_length=min(21, len(df)-1 if len(df)%2 == 0 else len(df)),
			# 	polyorder=3
			# )

			# kf = KalmanFilter(initial_state_mean=df['value'].iloc[0],
			# 	transition_matrices=[1],
			# 	observation_matrices=[1],
			# 	observation_covariance=0.5,
			# 	transition_covariance=0.01)
			# df['value'], _ = kf.filter(df['value'].values)

			# Расчет времени жизни
			df['lifetime'] = calculate_lifetime(df)
			
			# Построение графиков
			tag = df['tag'].iloc[0] if not df['tag'].isnull().all() else os.path.basename(file_path)
			
			ax1.plot(df['timestamp'], df['value'], label=f'{tag} (ток)', linewidth=1)
			ax2.plot(df['timestamp'], df['lifetime'], label=f'{tag} (время жизни)', color='red', linewidth=1)
		
		# Оформление графиков
		ax1.set_ylabel('Ток пучка [A]', fontsize=12)
		ax2.set_ylabel('Время жизни [часы]', fontsize=12)
		ax2.set_xlabel('Время', fontsize=12)
		
		# Форматирование оси времени с миллисекундной точностью
		date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S.%f')
		ax1.xaxis.set_major_formatter(date_format)
		fig.autofmt_xdate(rotation=45)
		
		# Улучшенное отображение сетки
		for ax in [ax1, ax2]:
			ax.grid(True, linestyle='--', alpha=0.6)
			ax.legend(fontsize=10)
			ax.tick_params(axis='both', which='major', labelsize=10)
		
		plt.suptitle('Мониторинг тока и времени жизни пучка (миллисекундное разрешение)', fontsize=14)
		plt.tight_layout()
		
		if output_image:
			plt.savefig(output_image, dpi=300, bbox_inches='tight')
			print(f"График сохранен в: {output_image}")
		
		if output_csv:
			df[['timestamp', 'value', 'lifetime']].to_csv(output_csv, index=False)
			print(f"Данные сохранены в: {output_csv}")
			
		plt.show()
		
	except Exception as e:
		print(f"Ошибка: {str(e)}")
		raise

# Пример использования
if __name__ == "__main__":
	plot(
		file_list=['./i5beam_5_days/beam_data_2025-07-03.csv'],
		output_image='beam_lifetime_ms.png',
		output_csv='beam_lifetime_ms.csv'
	)