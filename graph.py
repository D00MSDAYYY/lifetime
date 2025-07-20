import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import savgol_filter
import os

def plot(file_list, output_image=None):
	"""
	Фильтрация шумов и построение графиков с очищенными данными
	
	Параметры:
	file_list - список файлов с данными
	output_image - путь для сохранения графика
	"""
	try:
		plt.figure(figsize=(60, 30))
		
		for file_path in file_list:
			# Чтение данных с учетом формата
			df = pd.read_csv(
				file_path, 
				sep=';', 
				header=None,
				usecols=[0, 1, 2],  # Явно указываем какие столбцы читать (игнорируем последний пустой)
				names=['tag', 'timestamp', 'value'],
				engine='python'
			)
			
			# Очистка данных
			df = df.dropna(how='all')  # Удаление полностью пустых строк
			
			# Преобразование времени
			df['timestamp'] = pd.to_datetime(
				df['timestamp'].str.strip(),  # Удаляем пробелы
				format='%Y-%m-%d %H:%M:%S.%f'
			)

			# Удаление некорректных данных
			df = df.dropna(subset=['timestamp', 'value'])
			
			# Сглаживание данных
			# df['filtered'] = savgol_filter( #savgol
			# 	df['value'],
			# 	window_length=min(21, len(df)-1 if len(df)%2 == 0 else len(df)),
			# 	polyorder=3
			# )
   
			window_size = min(15, len(df)//10 or 1)
			df['filtered'] = df['value'].rolling(
			window=window_size, 
			center=True, 
			min_periods=1
			).mean()
			
			# Построение графиков
			tag = df['tag'].iloc[0] if not df['tag'].isnull().all() else os.path.basename(file_path)
			
			plt.plot(
				df['timestamp'], 
				df['value'], 
				alpha=0.3,
				label=f'{tag} (raw)',
				color='gray'
			)
			
			plt.plot(
				df['timestamp'], 
				df['filtered'], 
				label=f'{tag} (filtered)',
				linewidth=2
			)
		
		# Оформление графика
		ax = plt.gca()
		ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
		ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=30) )
		
		plt.xlabel('Time', fontsize=12)
		plt.grid(True, linestyle='--', alpha=0.6)
		
		# Измененная легенда (меньше и под графиком)
		plt.legend(
			fontsize=8,  # Уменьшенный размер шрифта
			loc='upper center',  # Расположение по центру
			bbox_to_anchor=(0.5, -0.1),  # Под графиком
			ncol=2  # Две колонки для компактности
		)
		
		plt.tight_layout()
		
		if output_image:
			plt.savefig(output_image, dpi=300, bbox_inches='tight')
			print(f"Graph saved to: {output_image}")
		else:
			plt.show()
			
		plt.close()
		
	except Exception as e:
		print(f"Error: {str(e)}")

# Пример использования
if __name__ == "__main__":
	data_files = [
		'./i5lifetime_5_days/beam_data_2025-06-30.csv',
		'./i5beam_5_days/beam_data_2025-06-30.csv'
	]
	
	plot(
		file_list=data_files,
		output_image='plot.png'
	)