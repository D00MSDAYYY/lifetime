import pandas as pd

def remove_half_second_data(csv_file_path, output_file_path=None):
    """
    Удаляет записи с временными метками, оканчивающимися на .5 секунды
    из CSV файла с данными тока пучка.
    
    Parameters:
    csv_file_path (str): путь к исходному CSV файлу
    output_file_path (str): путь для сохранения результата (опционально)
    """
    
    # Загружаем данные
    print(f"Загрузка данных из {csv_file_path}...")
    df = pd.read_csv(csv_file_path, sep=';', header=None, 
                    names=['signal_name', 'timestamp', 'current'])
    
    print(f"Найдено {len(df)} записей")
    
    # Конвертируем timestamp в datetime
    df['datetime'] = pd.to_datetime(df['timestamp'])
    
    # Извлекаем миллисекунды из временной метки
    df['milliseconds'] = df['datetime'].dt.microsecond / 1000
    df['seconds'] = df['datetime'].dt.second
    
    # Определяем, оканчивается ли время на .5 секунды
    # Проверяем, что секунды имеют .5 и миллисекунды близки к 0
    df['is_half_second'] = (df['seconds'] % 1 == 0.5) & (df['milliseconds'] < 50)
    
    # Альтернативный метод: проверяем по строковому представлению
    df['timestamp_str'] = df['timestamp'].astype(str)
    df['ends_with_5'] = df['timestamp_str'].str.endswith('5000000')
    
    # Фильтруем данные - оставляем только записи НЕ оканчивающиеся на .5
    df_filtered = df[~df['ends_with_5']].copy()
    
    # Удаляем временные колонки
    df_filtered = df_filtered[['signal_name', 'timestamp', 'current']]
    
    # Сохраняем результат
    if output_file_path is None:
        output_file_path = csv_file_path.replace('.csv', '_no_half_second.csv')
    
    df_filtered.to_csv(output_file_path, index=False, header=False, sep=';')
    
    print(f"Удалено записей с .5 секундами: {len(df) - len(df_filtered)}")
    print(f"Оставлено записей: {len(df_filtered)}")
    print(f"Результат сохранен в: {output_file_path}")
    
    return df_filtered

remove_half_second_data("../data/beam/misc/2025-06-30.csv"  )