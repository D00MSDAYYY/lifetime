import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Чтение данных из CSV файла
def read_sensor_data(filename):
    """
    Чтение данных из CSV файла с форматом:
    BN_CONTROL.I5BEAM;2025-06-30 16:32:41.0000000;24.917191
    """
    # Читаем файл, указывая разделитель и что нет заголовков
    df = pd.read_csv(filename, 
                     sep=';', 
                     header=None, 
                     names=['sensor_name', 'timestamp', 'value'])
    
    # Преобразуем timestamp в datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Преобразуем значение в float
    df['value'] = df['value'].astype(float)
    
    return df

# Построение графика
def plot_sensor_data(df, sensor_name=None):
    """
    Построение графика данных датчика
    
    Parameters:
    df - DataFrame с данными
    sensor_name - имя датчика для заголовка (опционально)
    """
    plt.figure(figsize=(12, 6))
    
    plt.plot(df['timestamp'], df['value'], 
             linewidth=1, marker='o', markersize=2, label='Данные датчика')
    
    # Настройка внешнего вида графика
    plt.xlabel('Время')
    plt.ylabel('Значение')
    
    if sensor_name:
        plt.title(f'Данные датчика: {sensor_name}')
    else:
        plt.title('Данные датчика')
    
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Форматирование оси времени для лучшей читаемости
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.show()

# Основная программа
if __name__ == "__main__":
    # Укажите путь к вашему файлу
    filename = '../data/beam/misc/2025-06-30.csv'  # замените на путь к вашему файлу
    
    try:
        # Чтение данных
        df = read_sensor_data(filename)
        # Построение графика
        plot_sensor_data(df, df['sensor_name'].iloc[0])
        
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")