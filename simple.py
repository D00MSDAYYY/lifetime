import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from scipy.signal import savgol_filter
from pykalman import KalmanFilter

# Физические константы
e = 1.6e-19  # элементарный заряд [Кл]

def calculate_lifetime(df_current, revolution_freq=2.38e6):
	"""
	Расчет времени жизни пучка через экспоненциальный распад
	с учетом миллисекундного разрешения временных меток
	
	Параметры:
	df_current - DataFrame с данными о токе
	revolution_freq - частота обращения частиц [Гц]
	
	Возвращает:
	Series с временем жизни в часах
	"""
	df = df_current.copy()
	# Конвертируем ток в число частиц
	df['N'] = df_current['value'] / (e * revolution_freq)
	
	# Вычисляем разницу между текущим и предыдущим значением
	df['delta_t'] = df_current['timestamp'].diff().dt.total_seconds()
	
	# Расчет tau по формуле: N_curr = N_0 * exp(-Δt/τ)
	with np.errstate(divide='ignore', invalid='ignore'):
		df['tau'] = -df['delta_t'] / np.log(df['N'] / df['N'].shift(1))
	
	# Переводим секунды в часы и убираем выбросы
	df['tag'] = "calculated_lifetime"
	df['value'] = df['tau'] / 3600
	df['value'] = df['value'].where(df['value'].between(0, 1000))  # Фильтр нереальных значений
	
	return df

def df_from_file(file_path):
	"""
	Загрузка данных из файла
	"""
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
	
	# Преобразование данных
	df['timestamp'] = pd.to_datetime(
		df['timestamp'].str.strip(),
		format='%Y-%m-%d %H:%M:%S.%f',
		errors='coerce'
	)
	
	df['value'] = pd.to_numeric(
		df['value'].astype(str).str.strip().str.replace(',', '.'),
		errors='coerce'
	)
	
	df.dropna(subset=['timestamp', 'value'], inplace=True)
	return df

def plot(df_list, output_image=None, output_csv=None):
	"""
	Построение графиков тока и времени жизни пучка с миллисекундным разрешением
	Каждый график выводится в отдельном ряду
	"""
	try:
		# Создаем subplots по количеству переданных DataFrame
		fig, axes = plt.subplots(len(df_list), 1, figsize=(20, 6*len(df_list)), sharex=True)
		
		# Если передан только один DataFrame, axes будет не массивом, а одиночным объектом
		if len(df_list) == 1:
			axes = [axes]
		
		for i, (df, ax) in enumerate(zip(df_list, axes)):
			# Удаление строк с NaN значениями
			df.dropna(subset=['timestamp', 'value'], inplace=True)

			# Построение графиков
			tag = df['tag'].iloc[0] 
			
			# График тока
			ax.plot(df['timestamp'], df['value'], label=f'{tag}', linewidth=1)
			ax.grid(True, linestyle='--', alpha=0.6)
			ax.legend(fontsize=10)
			ax.tick_params(axis='both', which='major', labelsize=10)
		
		# Общие настройки для всех графиков
		axes[-1].set_xlabel('Время', fontsize=12)
		date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
		axes[0].xaxis.set_major_formatter(date_format)
		fig.autofmt_xdate(rotation=45)
		plt.suptitle('Мониторинг параметров пучка', fontsize=14)
		plt.tight_layout()
		
		if output_image:
			plt.savefig(output_image, dpi=300, bbox_inches='tight')
			print(f"График сохранен в: {output_image}")
		
		if output_csv:
			combined_df = pd.concat(df_list)
			combined_df.to_csv(output_csv, index=False)
			print(f"Данные сохранены в: {output_csv}")
			
		plt.show()
		
	except Exception as e:
		print(f"Ошибка: {str(e)}")
		raise
	

def auto_window_size(df_series, max_window=31):
	std = df_series.std()
	if std < 0.1 * df_series.mean():
		return min(5, max_window)  # Мало шума
	else:
		return min(max(7, int(len(df_series)/1000)), max_window)

def auto_filter(df, window_size=None):

	if window_size is None:
		window_size = auto_window_size(df['value'])

	print(window_size)

	df_copy = df.copy()
	df_copy['value'] = df['value'].rolling(
		window=window_size, 
		center=True, 
		min_periods=1
	).mean()

	return df_copy
		


if __name__ == "__main__":
	# Загрузка данных
	df_current = auto_filter(df_from_file('./i5beam_5_days/beam_data_2025-07-02.csv'),50)
	df_predefined_lifetime = auto_filter(df_from_file('./i5lifetime_5_days/beam_data_2025-07-02.csv'),50)


	df_calculated_lifetime = auto_filter(calculate_lifetime(df_current),300)

	plot(
		df_list=[df_current,
				df_predefined_lifetime,
				df_calculated_lifetime],
		output_image='plot.png'
	)