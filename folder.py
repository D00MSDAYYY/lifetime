import os
import pandas as pd
from datetime import datetime, timedelta

def split_data_by_time(input_file, output_dir, time_interval_seconds):
    """
    Разделяет данные из исходного файла на отдельные файлы по заданным интервалам времени,
    обрабатывая случаи с отсутствующими значениями тока.
    
    Args:
        input_file (str): Путь к входному файлу
        output_dir (str): Директория для сохранения результатов
        time_interval_seconds (int): Интервал разбиения в секундах
    """
    try:
        if not output_dir:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_dir = f"{base_name}_split"

        # Создаем директорию, если ее нет
        os.makedirs(output_dir, exist_ok=True)
        
        # Читаем данные из файла, обрабатывая пустые значения
        df = pd.read_csv(input_file, sep=';', header=None,
                        names=['sensor', 'timestamp', 'current'],
                        decimal=',', na_filter=True,
                        na_values=['', ' ', 'NA', 'N/A'])
        
        # Заменяем NaN на пустую строку (как в исходном файле)
        df['current'] = df['current'].fillna('')
        
        # Преобразуем timestamp в datetime
        df['datetime'] = pd.to_datetime(df['timestamp'])
        
        # Вычисляем временные интервалы
        start_time = df['datetime'].min()
        df['time_bin'] = ((df['datetime'] - start_time).dt.total_seconds() // time_interval_seconds).astype(int)
        
        # Группируем данные по временным интервалам
        grouped = df.groupby('time_bin')
        
        # Обрабатываем каждый интервал отдельно
        for time_bin, interval_data in grouped:
            # Вычисляем временной диапазон для имени файла
            interval_start = start_time + timedelta(seconds=time_bin * time_interval_seconds)
            interval_end = interval_start + timedelta(seconds=time_interval_seconds)
            
            # Формируем имя файла
            start_str = interval_start.strftime('%Y-%m-%d_%H-%M-%S')
            end_str = interval_end.strftime('%H-%M-%S')
            output_file = os.path.join(output_dir, f'beam_data_{start_str}_to_{end_str}.csv')
            
            # Сохраняем данные в исходном формате
            with open(output_file, 'w', encoding='utf-8') as f:
                for _, row in interval_data.iterrows():
                    line = f"{row['sensor']};{row['timestamp']};{row['current']}\n"
                    f.write(line)
            
            print(f'Создан файл: {output_file}')
            
        print(f'\nВсего создано {len(grouped)} файлов в директории {output_dir}')
        
    except FileNotFoundError:
        print(f"Ошибка: файл {input_file} не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

# Примеры использования:

N = 60 * 60 * 24 
split_data_by_time('./beam_data/i5beam.csv', None, N)
split_data_by_time('./beam_data/i5lifetime.csv', None, N)

