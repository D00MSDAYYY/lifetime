import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

def plot_multiple_graphs_from_files(file_list, output_image=None):
    """
    Строит несколько графиков на одной картинке из списка файлов
    
    Параметры:
    file_list - список путей к файлам с данными (каждый файл содержит: тэг; время; значение)
    output_image - путь для сохранения графика (None - показать на экране)
    """
    try:
        # Создаем фигуру для всех графиков
        plt.figure(figsize=(15, 8))
        
        # Обрабатываем каждый файл
        for file_path in file_list:
            # Читаем данные
            df = pd.read_csv(
                file_path, 
                sep=';', 
                header=None,
                names=['tag', 'timestamp', 'value'],
                decimal=',', 
                na_values=['', ' ', 'NA', 'N/A']
            )
            
            # Преобразуем время и значения
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Извлекаем уникальный тэг (название графика)
            tag = df['tag'].iloc[0] if not df['tag'].isnull().all() else os.path.basename(file_path)
            
            # Строим график
            plt.plot(
                df['timestamp'], 
                df['value'], 
                label=tag,
                linewidth=1,
                marker='o' if len(df) < 100 else None  # маркеры только для коротких рядов
            )
        
        # Настраиваем общий график
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        plt.xlabel('Время', fontsize=12)
        plt.ylabel('Значение', fontsize=12)
        plt.title('Сравнение показателей', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')  # легенда справа
        
        plt.tight_layout()
        
        # Сохраняем или показываем
        if output_image:
            plt.savefig(output_image, dpi=300, bbox_inches='tight')
            print(f"График сохранен в: {output_image}")
        else:
            plt.show()
            
        plt.close()
        
    except Exception as e:
        print(f"Ошибка при построении графиков: {str(e)}")

# Пример использования
if __name__ == "__main__":
    files = [
        'i5energy_5_days/beam_data_2025-06-30.csv'
    ]
    
    plot_multiple_graphs_from_files(
        file_list=files,
        output_image='combined_graphs.png'
    )