import math
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import CONSTANTS

from scipy import constants
from scattering.simple import simple_scattering
from scattering.coulumb import coulomb_scattering_wiedermann

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

	df_copy = df.copy()
	df_copy['value'] = df['value'].rolling(
		window=window_size, 
		center=True, 
		min_periods=1
	).mean()

	return df_copy
		


if __name__ == "__main__":
	# ################################################################################

	df_current = auto_filter(df_from_file('./i5beam_5_days/beam_data_2025-07-02.csv'),50)
	df_predefined_lifetime = auto_filter(df_from_file('./i5lifetime_5_days/beam_data_2025-07-02.csv'),50)

	# df_simple_lifetime = auto_filter(simple_scattering(df_current,CONSTANTS.siberia2.RevolutionFrequency),300)
	# plot(
	# 	df_list=[df_current,
	# 			df_predefined_lifetime,
	# 			df_simple_lifetime],
	# 	output_image='./plots/simple.png'
	# )
	
	# ################################################################################

	# Параметры для расчёта времени жизни (пример для электронного пучка в N₂)
	beta = 1       # ≈1 для релятивистских частиц
	P_Torr = CONSTANTS.siberia2.P_Torr          # Давление [Торр] (пример для сверхвысокого вакуума)
	z = 1                  # Заряд электрона
	Z = 7                  # Заряд ядра азота
	theta_max =  math.sqrt(CONSTANTS.siberia2.eA  /  CONSTANTS.siberia2.AverageBetatronFunction )  # Максимальный угол рассеяния [рад]

	# Предположим, что импульс p = 2.5 ГэВ/c (переводим в CGS: 1 ГэВ/c ≈ 1.602e-2 г·см/с)
	p_gev = CONSTANTS.siberia2.Energy_GeV            # Импульс (приблизительно) [ГэВ/c]
	p_cgs = p_gev * 1.602e-2  # Импульс [г·см/с]

	# Расчёт времени жизни
	tau_hours = coulomb_scattering_wiedermann(beta, P_Torr, z, Z, p_cgs, theta_max)

	# Создаём DataFrame с расчётным временем жизни (для визуализации)
	df_calculated_lifetime = df_current.copy()
	df_calculated_lifetime['value'] = tau_hours  # Просто постоянное значение для примера

	# Визуализация
	plot(
		df_list=[df_current,
				df_predefined_lifetime,
				df_calculated_lifetime],
		output_image='./plots/coulomb_scattering.png'
	)

	

	# ################################################################################



