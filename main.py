import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import savgol_filter
import os

def clean_and_plot(file_list, output_image=None):
    """
    Фильтрация шумов и построение графиков с очищенными данными
    
    Параметры:
    file_list - список файлов с данными
    output_image - путь для сохранения графика
    """
    try:
        plt.figure(figsize=(15, 8))
        
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
            
            # Преобразование значений (замена запятых на точки для дробных чисел)
            df['value'] = pd.to_numeric(
                df['value'].astype(str).str.replace(',', '.'), 
                errors='coerce'
            )
            
            # Удаление некорректных данных
            df = df.dropna(subset=['timestamp', 'value'])
            
            # Фильтрация физически невозможных значений (ток не может быть отрицательным)
            if 'beam' in df['tag'].iloc[0].lower():
                df = df[df['value'] >= 0]
            
            # Сглаживание данных
            window_size = min(15, len(df)//10 or 1)
            df['smoothed'] = df['value'].rolling(
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
                df['smoothed'], 
                label=f'{tag} (filtered)',
                linewidth=2
            )
        
        # Оформление графика
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Beam Current', fontsize=12)
        plt.title('Beam Current Monitoring (Filtered)', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
        
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
        './i5beam_5_days/beam_data_2025-06-30.csv',  # Укажите ваш файл
    ]
    
    clean_and_plot(
        file_list=data_files,
        output_image='beam_current_filtered.png'
    )