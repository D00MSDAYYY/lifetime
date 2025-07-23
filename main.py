import math
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import CONFIG

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
			
			ax.plot(df['timestamp'], df['value'], label=f'{tag}', linewidth=1)
			ax.grid(True, linestyle='--', alpha=0.6)
			ax.legend(fontsize=10)
			ax.tick_params(axis='both', which='major', labelsize=10)
		
		# Общие настройки для всех графиков
		axes[-1].set_xlabel('Время', fontsize=12)
		date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
		axes[0].xaxis.set_major_formatter(date_format)
		fig.autofmt_xdate(rotation=45)
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

def auto_filter(df, window_size=None):

	def auto_window_size(df_series, max_window=31):
		std = df_series.std()
		if std < 0.1 * df_series.mean():
			return min(5, max_window) 
		else:
			return min(max(7, int(len(df_series)/1000)), max_window)
	
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

	df_current_predefined = auto_filter(df_from_file('./i5beam_5_days/beam_data_2025-07-02.csv'),50)
	df_lifetime_predefined = auto_filter(df_from_file('./i5lifetime_5_days/beam_data_2025-07-02.csv'),50)

	# ################################################################################

	# df_lifetime_simple = auto_filter(simple_scattering(df_current_predefined, 
	# 												CONFIG.siberia2.RevolutionFrequency), 
	# 								300)

	# plot(
	# 	df_list=[
	# 		df_current_predefined,
	# 		df_lifetime_predefined,
	# 		df_lifetime_simple
	# 		],
	# 	output_image='./plots/coulumb_simple.png'
	# )
	
	# ################################################################################

	theta_max =  math.sqrt(CONFIG.siberia2.eA / CONFIG.siberia2.AverageBetatronFunction)   # Максимальный угол рассеяния [рад]

	coulomb_tau_hours = coulomb_scattering_wiedermann(CONFIG.siberia2.beta, 
														CONFIG.siberia2.P_Torr, 
														CONFIG.z,
														CONFIG.Z_avg,
														CONFIG.siberia2.Energy_GeV,
														theta_max)

	df_coulomb_lifetime_wiedermann = df_current_predefined.copy()
	df_coulomb_lifetime_wiedermann['tag'] = 'coulomb_wiedermann'
	df_coulomb_lifetime_wiedermann['value'] = coulomb_tau_hours  # Просто постоянное значение для примера
	print(df_coulomb_lifetime_wiedermann)

	df_lifetime_zaycev = coulomb_scattering_zaycev(df_current_predefined, 
												CONFIG.siberia2.RevolutionFrequency,
												CONFIG.siberia2.beta, 
												CONFIG.siberia2.P_Torr,
												CONFIG.z, 
												CONFIG.Z_avg, 
												CONFIG.siberia2.Energy_GeV, 
												theta_max)
	# Визуализация
	plot(
		df_list=[df_current_predefined,
				df_lifetime_predefined,
				df_coulomb_lifetime_wiedermann,
				df_lifetime_zaycev
				],
		output_image='./plots/coulomb_wiedermann_zaycev.png'
	)

# 	# ################################################################################

# 	# Предполагаемые параметры (замените на актуальные из CONSTANTS.siberia2)
# 	beta = 1                          # v/c ≈ 1 для релятивистских электронов
# 	nZ = 2                             # Для N₂ (азот, двухатомный газ)
# 	Z = 7                              # Заряд ядра азота
# 	A_acceptance_mm_mrad = CONSTANTS.siberia2.eA  
# 	beta_func_value_m = 7  # Бета-функция [м]
# 	gamma =  CONSTANTS.siberia2.Energy_GeV / 0.511e-3  # γ = E/mc² (для электронов 0.511 МэВ)

# 	# Вызов функции
# 	tau_hours = coulomb_scattering_chao(
# 		beta=beta,
# 		nZ=nZ,
# 		Z=Z,
# 		A_acceptance=A_acceptance_mm_mrad,
# 		beta_func_value=beta_func_value_m,
# 		gamma=gamma
# 	)
	
# 	df_coulomb_chao_lifetime = df_current.copy()
# 	df_coulomb_chao_lifetime['tag'] = 'coulumb_chao'
# 	df_coulomb_chao_lifetime['value'] = tau_hours  # Просто постоянное значение для примера
	
# 	# plot(
# 	# 	df_list=[df_current,
# 	# 			df_predefined_lifetime,
# 	# 			df_coulomb_wiedermann_lifetime,
# 	# 			df_chao_lifetime
# 	# 			],
# 	# 	output_image='./plots/coulomb_scattering.png'
# 	# )
# 	# ################################################################################

# 	alpha, _, _ = constants.physical_constants['fine-structure constant']
# 	re, _, _ = constants.physical_constants['classical electron radius']

# 	# Средняя атомная масса




# 	L_rad = math.log( 184.15 * Z_eff**( -1 / 3 ) )

# 	a = alpha * Z_eff
# 	func_z = a**2 * ( ( 1 + a**2 )**(-1) + 0.20206 - 0.0369 * a**2 + 0.0083 * a**4 - 0.002 * a**6 )
	
# 	L_apostrophe_rad = math.log( 1194 * Z_eff**( -2 / 3 ) )

# 	tmp_braces = Z_eff**2 * ( L_rad - func_z ) + Z_eff * L_apostrophe_rad

# 	tmp_inv =  4 * alpha * re**2 * ( constants.Avogadro / A_avg ) * tmp_braces

# 	X0 = 1 / tmp_inv
# 	dp_p_lim_acceptance = 0.02 # от балды взял от дипсика

# 	beta = 1

# 	n_Z_avg = sum(gas["fraction"] * gas["n_Z"] for gas in gases.values())

# 	bremstahlung_tau_hours = bremstahlung_scattering_chao(beta,n_Z_avg, A_avg, X0, dp_p_lim_acceptance )

# 	df_brem_chao_lifetime = df_current.copy()
# 	df_brem_chao_lifetime['tag'] = 'bremstahlung_chao'
# 	df_brem_chao_lifetime['value'] = bremstahlung_tau_hours  

# 	df_col_and_brem = df_current.copy()
# 	df_col_and_brem['tag'] = 'col_and_brem'
# 	df_col_and_brem['value'] = 1 / ( 1 / bremstahlung_tau_hours + 1 / coulomb_tau_hours ) 

# 	plot(
# 		df_list=[df_current,
# 				df_predefined_lifetime,
# 				df_coulomb_chao_lifetime,
# 				df_brem_chao_lifetime
# 				],
# 		output_image='./plots/coulomb_scattering.png'
# 	)











