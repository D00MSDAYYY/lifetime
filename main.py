import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

def plot_daily_beam_current(input_file, output_image=None):
    """
    Строит график тока пучка за день из файла данных
    
    Параметры:
    input_file - путь к файлу с данными за день
    output_image - путь для сохранения графика (None - показать на экране)
    """
    try:
        # Чтение данных с обработкой пустых значений
        df = pd.read_csv(input_file, sep=';', header=None,
                        names=['sensor', 'timestamp', 'current'],
                        decimal=',', na_values=['', ' ', 'NA', 'N/A'])
        
        # Преобразование времени и обработка пустых значений
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['current'] = pd.to_numeric(df['current'], errors='coerce')  # преобразуем в числа
        
        # Создание графика
        plt.figure(figsize=(15, 6))
        
        # Основной график тока
        plt.plot(df['timestamp'], df['current'], 
                'b-', linewidth=1, label='Ток пучка')
        
        # Настройка осей
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Подписи и оформление
        plt.xlabel('Время', fontsize=12)
        plt.ylabel('Ток пучка, А', fontsize=12)
        
        # Извлекаем дату из первого значения
        date_str = df['timestamp'].iloc[0].strftime('%Y-%m-%d')
        plt.title(f'Ток пучка за {date_str}', fontsize=14)
        
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(fontsize=10)
        
        # Оптимизация размещения
        plt.tight_layout()
        
        # Сохранение или отображение
        if output_image:
            plt.savefig(output_image, dpi=300)
            print(f"График сохранен в файл: {output_image}")
        else:
            plt.show()
            
        plt.close()
        
    except Exception as e:
        print(f"Ошибка при построении графика: {str(e)}")

# Пример использования:
# Для одного файла:
# plot_daily_beam_current('beam_data_2025-06-30.csv', 'beam_current_2025-06-30.png')

# Для всех файлов в папке:
import glob

def plot_all_days(data_folder, output_folder='daily_plots'):
    """Строит графики для всех файлов в папке"""
    os.makedirs(output_folder, exist_ok=True)
    
    for day_file in glob.glob(os.path.join(data_folder, 'beam_data_*.csv')):
        date_str = os.path.basename(day_file)[10:-4]  # извлекаем дату из имени файла
        output_file = os.path.join(output_folder, f'beam_current_{date_str}.png')
        plot_daily_beam_current(day_file, output_file)


plot_all_days('./i5beam_5_days')