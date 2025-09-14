import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
from filtering.moving_average import moving_average

def load_beam_current_data(csv_file_path):
    """
    Загружает данные о силе тока пучка из CSV файла.
    Формат: BN_CONTROL.I5BEAM;timestamp;current_value
    """
    # Загружаем данные, игнорируя первую колонку (она всегда одинаковая)
    df = pd.read_csv(csv_file_path, sep=';', header=None, 
                    names=['signal_name', 'timestamp', 'current'])
    
    # Конвертируем timestamp в datetime
    df['datetime'] = pd.to_datetime(df['timestamp'])
    
    # Сортируем по времени (на всякий случай)
    df = df.sort_values('datetime')
    
    # Вычисляем временные метки в секундах относительно начала
    start_time = df['datetime'].iloc[0]
    df['time_seconds'] = (df['datetime'] - start_time).dt.total_seconds()
    
    # Вычисляем частоту дискретизации
    time_diff = np.diff(df['time_seconds'])
    sampling_rate = 1 / np.mean(time_diff) if len(time_diff) > 0 else 1
    
    print(f"Загружено {len(df)} записей")
    print(f"Начальное время: {start_time}")
    print(f"Частота дискретизации: {sampling_rate:.2f} Гц")
    print(f"Длительность сигнала: {df['time_seconds'].iloc[-1]:.2f} секунд")
    print(f"Диапазон тока: от {df['current'].min():.6f} до {df['current'].max():.6f} А")
    
    return df, sampling_rate

def analyze_beam_current_dft(df, sampling_rate):
    """
    Анализирует сигнал тока с помощью DFT и строит графики.
    """
    current_data = df['current'].values
    time_data = df['time_seconds'].values
    
    # Вычисляем DFT
    n = len(current_data)
    dft_result = np.fft.fft(current_data)
    frequencies = np.fft.fftfreq(n, 1/sampling_rate)
    
    # Берем первую половину (симметричный спектр)
    half_n = n // 2
    frequencies_half = frequencies[:half_n]
    magnitude = np.abs(dft_result[:half_n]) / n
    # magnitude = moving_average(magnitude, 40)
    magnitude_db = 20 * np.log10(magnitude + 1e-10)  # В дБ для лучшей видимости
    
    # Создаем figure с subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Исходный сигнал во временной области
    ax1.plot(time_data, current_data, 'b-', linewidth=1, alpha=0.8)
    ax1.set_xlabel('Время (с)')
    ax1.set_ylabel('Сила тока (А)')
    ax1.set_title('Исходный сигнал силы тока пучка')
    ax1.grid(True, alpha=0.3)
    
    # 2. Сигнал в логарифмическом масштабе по Y
    ax2.semilogy(time_data, np.abs(current_data), 'r-', linewidth=1, alpha=0.8)
    ax2.set_xlabel('Время (с)')
    ax2.set_ylabel('|Ток| (А) - лог. шкала')
    ax2.set_title('Сигнал в логарифмическом масштабе')
    ax2.grid(True, alpha=0.3, which='both')
    
    # 3. Амплитудный спектр (линейная шкала)
    ax3.plot(frequencies_half, magnitude, 'g-', linewidth=1)
    ax3.set_xlabel('Частота (Гц)')
    ax3.set_ylabel('Амплитуда')
    ax3.set_title('Амплитудный спектр (DFT) - Линейная шкала')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, min(1, frequencies_half[-1]))  # Ограничиваем для видимости
    
    # 4. Амплитудный спектр (логарифмическая шкала - дБ)
    ax4.plot(frequencies_half, magnitude_db, 'm-', linewidth=1)
    ax4.set_xlabel('Частота (Гц)')
    ax4.set_ylabel('Амплитуда (дБ)')
    ax4.set_title('Амплитудный спектр (DFT) - Логарифмическая шкала')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, min(1, frequencies_half[-1]))
    
    plt.tight_layout()
    plt.show()
    
    return fig, frequencies_half, magnitude, magnitude_db

def analyze_frequency_peaks(frequencies, magnitude_db, min_height=-40, min_prominence=1):
    """
    Анализирует и выводит информацию о пиках в спектре.
    """
    # Ищем пики в частотном спектре
    peak_indices, properties = signal.find_peaks(
        magnitude_db, 
        height=min_height, 
        prominence=min_prominence
    )
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЧАСТОТНЫХ КОМПОНЕНТОВ")
    print("="*50)
    
    if len(peak_indices) == 0:
        print("Значимых пиков не обнаружено")
        return
    
    # Сортируем пики по амплитуде (по убыванию)
    sorted_peaks = sorted(zip(peak_indices, properties['peak_heights']), 
                         key=lambda x: x[1], reverse=True)
    
    for i, (idx, height) in enumerate(sorted_peaks[:10]):  # Топ-10 пиков
        freq = frequencies[idx]
        if freq >= 0:  # Игнорируем отрицательные частоты
            print(f"Пик {i+1}: {freq:.4f} Гц - {height:.1f} дБ")
            
            # Определяем тип пика
            if abs(freq) < 0.001:
                print("     → Постоянная составляющая (DC)")
            elif freq < 0.01:
                print("     → Очень низкочастотные колебания")
            elif freq < 0.1:
                print("     → Низкочастотные колебания")
            else:
                print("     → Высокочастотные компоненты")


def main(csv_file_path):
    """
    Основная функция анализа.
    """
    # Загрузка данных

    df, sampling_rate = load_beam_current_data(csv_file_path)

    print(f"Частота Найквиста: {0.5 * sampling_rate:.3f} Гц")

    # DFT анализ
    print("\nВыполнение DFT анализа...")
    fig_dft, frequencies, magnitude, magnitude_db = analyze_beam_current_dft(df, sampling_rate)
    
    # Анализ частотных пиков
    analyze_frequency_peaks(frequencies, magnitude_db)


if __name__ == "__main__":

    csv_file_path = "../data/beam/misc/2025-07-03.csv"  
    
    try:
        main(csv_file_path)
    except FileNotFoundError:
        print(f"Файл {csv_file_path} не найден!")
        print("Проверьте путь к файлу.")