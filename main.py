import math
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import CONSTANTS

from scipy import constants
from scattering.simple import simple_scattering
from scattering.coulumb import coulomb_scattering_wiedermann, coulomb_scattering_zaycev, coulomb_scattering_chao
from scattering.bremstahlung import bremstahlung_scattering_chao

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
	theta_max =  CONSTANTS.siberia2.eA**2   /  CONSTANTS.siberia2.AverageBetatronFunction   # Максимальный угол рассеяния [рад]

	# Предположим, что импульс p = 2.5 ГэВ/c (переводим в CGS: 1 ГэВ/c ≈ 1.602e-2 г·см/с)
	p_gev = CONSTANTS.siberia2.Energy_GeV            # Импульс (приблизительно) [ГэВ/c]
	p_cgs = p_gev * 1.602e-2  # Импульс [г·см/с]

	# Расчёт времени жизни
	coulomb_tau_hours = coulomb_scattering_wiedermann(beta, P_Torr, z, Z, p_cgs, theta_max)

	# Создаём DataFrame с расчётным временем жизни (для визуализации)
	df_coulomb_wiedermann_lifetime = df_current.copy()
	df_coulomb_wiedermann_lifetime['tag'] = 'coulomb_wiedermann'
	df_coulomb_wiedermann_lifetime['value'] = coulomb_tau_hours  # Просто постоянное значение для примера
	print(df_coulomb_wiedermann_lifetime)
	# df_zaycev_lifetime = coulomb_scattering_zaycev(df_current, CONSTANTS.siberia2.RevolutionFrequency,beta, P_Torr, z, Z, p_cgs, theta_max)
	# # Визуализация
	# plot(
	# 	df_list=[df_current,
	# 			df_predefined_lifetime,
	# 			df_coulomb_wiedermann_lifetime,
	# 			df_zaycev_lifetime
	# 			],
	# 	output_image='./plots/coulomb_scattering.png'
	# )

	# ################################################################################

	# Предполагаемые параметры (замените на актуальные из CONSTANTS.siberia2)
	beta = 1                          # v/c ≈ 1 для релятивистских электронов
	nZ = 2                             # Для N₂ (азот, двухатомный газ)
	Z = 7                              # Заряд ядра азота
	A_acceptance_mm_mrad = CONSTANTS.siberia2.eA  
	beta_func_value_m = 7  # Бета-функция [м]
	gamma =  CONSTANTS.siberia2.Energy_GeV / 0.511e-3  # γ = E/mc² (для электронов 0.511 МэВ)

	# Вызов функции
	tau_hours = coulomb_scattering_chao(
		beta=beta,
		nZ=nZ,
		Z=Z,
		A_acceptance=A_acceptance_mm_mrad,
		beta_func_value=beta_func_value_m,
		gamma=gamma
	)
	
	df_coulomb_chao_lifetime = df_current.copy()
	df_coulomb_chao_lifetime['tag'] = 'coulumb_chao'
	df_coulomb_chao_lifetime['value'] = tau_hours  # Просто постоянное значение для примера
	
	# plot(
	# 	df_list=[df_current,
	# 			df_predefined_lifetime,
	# 			df_coulomb_wiedermann_lifetime,
	# 			df_chao_lifetime
	# 			],
	# 	output_image='./plots/coulomb_scattering.png'
	# )
	# ################################################################################

	alpha, _, _ = constants.physical_constants['fine-structure constant']
	re, _, _ = constants.physical_constants['classical electron radius']
	gases = {
    "H2": {
        "fraction": 0.7,    # Доля в смеси (70%)
        "mass": 2.016,      # Молекулярная масса [г/моль]
        "Z": 1,             # Атомный номер (для водорода Z=1)
        "n_Z": 2            # 2 атома H в молекуле H₂
    },
    "CO": {
        "fraction": 0.2,    # Доля в смеси (20%)
        "mass": 28.010,     # Молекулярная масса [г/моль]
        "Z": 7,             # Средний атомный номер (C=6 + O=8 → 7)
        "n_Z": 2            # 2 атома (1C + 1O)
    },
    "H2O": {
        "fraction": 0.1,    # Доля в смеси (10%)
        "mass": 18.015,     # Молекулярная масса [г/моль]
        "Z": 3.33,          # Средний атомный номер (2H + O → (2*1 + 8)/3 ≈ 3.33)
        "n_Z": 3            # 3 атома (2H + 1O)
    }
}
	# Средняя атомная масса
	A_avg = sum(gas["fraction"] * gas["mass"] for gas in gases.values())

	Z_squared_avg = sum(gas["fraction"] * gas["Z"]**2 for gas in gases.values())
	Z_eff = math.sqrt(Z_squared_avg)

	L_rad = math.log( 184.15 * Z_eff**( -1 / 3 ) )

	a = alpha * Z_eff
	func_z = a**2 * ( ( 1 + a**2 )**(-1) + 0.20206 - 0.0369 * a**2 + 0.0083 * a**4 - 0.002 * a**6 )
	
	L_apostrophe_rad = math.log( 1194 * Z_eff**( -2 / 3 ) )

	tmp_braces = Z_eff**2 * ( L_rad - func_z ) + Z_eff * L_apostrophe_rad

	tmp_inv =  4 * alpha * re**2 * ( constants.Avogadro / A_avg ) * tmp_braces

	X0 = 1 / tmp_inv
	dp_p_lim_acceptance = 0.02 # от балды взял от дипсика

	beta = 1

	n_Z_avg = sum(gas["fraction"] * gas["n_Z"] for gas in gases.values())

	bremstahlung_tau_hours = bremstahlung_scattering_chao(beta,n_Z_avg, A_avg, X0, dp_p_lim_acceptance )

	df_brem_chao_lifetime = df_current.copy()
	df_brem_chao_lifetime['tag'] = 'bremstahlung_chao'
	df_brem_chao_lifetime['value'] = bremstahlung_tau_hours  

	df_col_and_brem = df_current.copy()
	df_col_and_brem['tag'] = 'col_and_brem'
	df_col_and_brem['value'] = 1 / ( 1 / bremstahlung_tau_hours + 1 / coulomb_tau_hours ) 

	plot(
		df_list=[df_current,
				df_predefined_lifetime,
				df_coulomb_chao_lifetime,
				df_brem_chao_lifetime
				],
		output_image='./plots/coulomb_scattering.png'
	)











