import os
import pandas as pd
from datetime import datetime

def split_data_by_days(input_file):
    """
    Разделяет данные из исходного файла на отдельные файлы по дням,
    обрабатывая случаи с отсутствующими значениями тока.
    """
    try:
        # Получаем имя файла без расширения для создания папки
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = f"{base_name}_5_days"
        
        # Создаем директорию, если ее нет
        os.makedirs(output_dir, exist_ok=True)
        
        # Читаем данные из файла, обрабатывая пустые значения
        df = pd.read_csv(input_file, sep=';', header=None,
                        names=['sensor', 'timestamp', 'current'],
                        decimal=',', na_filter=True,
                        na_values=['', ' ', 'NA', 'N/A'])
        
        # Заменяем NaN на пустую строку (как в исходном файле)
        df['current'] = df['current'].fillna('')
        
        # Преобразуем timestamp в datetime и извлекаем дату
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Группируем данные по дням
        grouped = df.groupby('date')
        
        # Обрабатываем каждый день отдельно
        for date, day_data in grouped:
            # Формируем имя файла для этого дня
            date_str = date.strftime('%Y-%m-%d')
            output_filename = os.path.join(output_dir, f'beam_data_{date_str}.csv')
            
            # Сохраняем данные в исходном формате
            with open(output_filename, 'w') as f:
                for _, row in day_data.iterrows():
                    line = f"{row['sensor']};{row['timestamp']};{row['current']}\n"
                    f.write(line)
            
            print(f'Создан файл: {output_filename}')
            
        print(f'\nВсего создано {len(grouped)} файлов в директории {output_dir}')
        
    except FileNotFoundError:
        print(f"Ошибка: файл {input_file} не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

# Пример использования:

split_data_by_days('./beam_data/i5beam.csv')