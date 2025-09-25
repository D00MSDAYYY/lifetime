import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import CONSTANTS_CONFIG

from scattering.exponential_decay import exponential_decay_scattering
from scattering.pascal_adapted import pascal_scattering
from scattering.elastic import elactic_scattering_wiedemann, elactic_scattering_wiedemann2, elactic_scattering_chao, elactic_e
from scattering.bremstahlung import bremstahlung_scattering_wiedemann, bremstahlung_scattering_chao

class _aux_Data:
    pass
lifetime = _aux_Data()

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
	df['value'] = df['value'].where(df['value'] >= 0, 0)

	
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

	df_current_predefined = df_from_file('./data/beam/splitted_by_days/i5beam/beam_data_2025-06-30_00-00-00_to_00-00-00.csv')
	# lifetime.predefined = auto_filter(df_from_file('./i5lifetime_split/beam_data_2025-06-30_00-00-00_to_00-00-00.csv'),50)

	# ################################################################################

	# lifetime.simple = auto_filter(simple_scattering(df_current_predefined, 
	# 												CONSTANTS_CONFIG.siberia2.RevolutionFrequency), 250)
	
	# ################################################################################

	# lifetime.pascal = auto_filter(pascal_scattering(df_current_predefined), 400)

	# ################################################################################

	theta_max = 1e-2  # Фиксированное малое значение для оценки
	p_CGS = CONSTANTS_CONFIG.siberia2.gamma * CONSTANTS_CONFIG.siberia2.beta * CONSTANTS_CONFIG.CGS.e_mass * CONSTANTS_CONFIG.CGS.c
	lifetime.elactic_wiedemann = df_current_predefined.copy()
	lifetime.elactic_wiedemann['tag'] = 'elactic_wiedemann'
	lifetime.elactic_wiedemann['value'] = elactic_scattering_wiedemann(
														beta=CONSTANTS_CONFIG.siberia2.beta, 
														P_Torr=CONSTANTS_CONFIG.siberia2.P_Torr, 
														z=1,
														Z=CONSTANTS_CONFIG.Z_avg,
														p=p_CGS,
														theta_max=theta_max)

	# ################################################################################

	# lifetime.elactic_wiedemann2 = df_current_predefined.copy()
	# lifetime.elactic_wiedemann2['tag'] = 'elactic_wiedemann2'
	# lifetime.elactic_wiedemann2['value'] = elactic_scattering_wiedemann2( 2.5,
	# 																  CONSTANTS_CONFIG.siberia2.eA_mm_mrad,
	# 																  CONSTANTS_CONFIG.siberia2.AverageBetatronFunction,
	# 																  CONSTANTS_CONFIG.siberia2.P_Torr * 1e9 )

	# ################################################################################

	# lifetime.brem_wiedemann = df_current_predefined.copy()
	# lifetime.brem_wiedemann['tag'] = 'bremstahlung_wiedemann'
	# lifetime.brem_wiedemann['value'] = bremstahlung_scattering_wiedemann(
	# 													P_Torr=CONSTANTS_CONFIG.siberia2.P_Torr,
	# 													energy_acceptance=0.02)

 	# ################################################################################

	# lifetime.elactic_chao = df_current_predefined.copy()
	# lifetime.elactic_chao['tag'] = 'elactic_chao'
	# lifetime.elactic_chao['value'] = elactic_scattering_chao(
	# 	beta=CONSTANTS_CONFIG.siberia2.beta,
	# 	nZ=CONSTANTS_CONFIG.n_Z_avg,
	# 	Z=CONSTANTS_CONFIG.Z_avg,
	# 	A_acceptance=CONSTANTS_CONFIG.siberia2.eA,
	# 	beta_func_value=CONSTANTS_CONFIG.siberia2.AverageBetatronFunction,
	# 	gamma=CONSTANTS_CONFIG.siberia2.gamma,
	# 	P_Torr=CONSTANTS_CONFIG.siberia2.P_Torr,
	# 	T_K=290
	# ) 

	# ################################################################################

	# alpha, _, _ = CONSTANTS_CONFIG.constants.physical_constants['fine-structure constant']
	# re, _, _ = CONSTANTS_CONFIG.constants.physical_constants['classical electron radius']

	# L_rad = math.log( 184.15 * CONSTANTS_CONFIG.Z_avg**( -1 / 3 ) )

	# a = alpha * CONSTANTS_CONFIG.Z_avg

	# func_z = a**2 * ( ( 1 + a**2 )**(-1) + 0.20206 - 0.0369 * a**2 + 0.0083 * a**4 - 0.002 * a**6 )
	
	# L_apostrophe_rad = math.log( 1194 * CONSTANTS_CONFIG.Z_avg**( -2 / 3 ) )

	# tmp_braces = CONSTANTS_CONFIG.Z_avg**2 * ( L_rad - func_z ) + CONSTANTS_CONFIG.Z_avg * L_apostrophe_rad

	# tmp_inv =  4 * alpha * re**2 * ( CONSTANTS_CONFIG.constants.Avogadro / CONSTANTS_CONFIG.A_avg ) * tmp_braces

	# X0 = 1 / tmp_inv  # перевожу к размерности г см
	# print(X0)
	# X0 = 3725
	# lifetime.brem_chao = df_current_predefined.copy()
	# lifetime.brem_chao['tag'] = 'bremstahlung_chao'
	# lifetime.brem_chao['value'] = bremstahlung_scattering_chao(beta=CONSTANTS_CONFIG.siberia2.beta,
	# 															nZ=CONSTANTS_CONFIG.n_Z_avg,
	# 															A=10e-3,
	# 															X0=X0,
	# 															dp_p_lim_acceptance=0.02,  # от балды взял от дипсика
	# 															P_Torr=CONSTANTS_CONFIG.siberia2.P_Torr,
	# 															T_K=CONSTANTS_CONFIG.T_gas_K )  

	# ################################################################################

	# tau_e = elactic_e(CONSTANTS_CONFIG.siberia2.gamma,
	# 			   7,
	# 			   CONSTANTS_CONFIG.siberia2.AverageBetatronXFunction,
	# 			   CONSTANTS_CONFIG.siberia2.AverageBetatronYFunction,
	# 			   CONSTANTS_CONFIG.siberia2.AverageBetatronFunction,
	# 			   CONSTANTS_CONFIG.siberia2.HorizontalAperture,
	# 			   CONSTANTS_CONFIG.siberia2.VerticalAperture,
	# 			   CONSTANTS_CONFIG.siberia2.P_Torr)
	
	# ################################################################################


	plot(
		df_list=[
			# df_current_predefined
			# ,
			# lifetime.predefined,
			# lifetime.simple
			# ,
			# lifetime.pascal ,
			lifetime.elactic_wiedemann
			# ,
			# lifetime.elactic_wiedemann2
			# ,
			# lifetime.elactic_chao,
			# lifetime.brem_wiedemann,
			# lifetime.brem_chao
			],
		output_image='./plots/all.png'
	)
