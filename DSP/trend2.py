import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error

def exponential_decay(t, A, tau, C):
    """
    Модель экспоненциального затухания
    y = A * exp(-t/tau) + C
    где:
    A - начальная амплитуда
    tau - постоянная времени (характерное время затухания)
    C - постоянное смещение (асимптота)
    """
    return A * np.exp(-t / tau) + C

def fit_exponential_decay(df):
    # Подготовка данных
    # Преобразуем время в числовой формат (секунды от начала)
    time_numeric = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()
    y_data = df['value'].values
    
    # Начальное приближение для параметров
    A0 = y_data[0] - y_data[-1]  # начальная амплитуда
    tau0 = (time_numeric.iloc[-1] - time_numeric.iloc[0]) / 5  # начальная оценка tau
    C0 = y_data[-1]  # асимптотическое значение
    
    initial_guess = [A0, tau0, C0]
    
    try:
        # Нелинейная подгонка
        popt, pcov = curve_fit(exponential_decay, 
                              time_numeric, y_data, 
                              p0=initial_guess)
        
        A_fit, tau_fit, C_fit = popt
        errors = np.sqrt(np.diag(pcov))  # стандартные ошибки параметров
        
        # Расчет предсказанных значений
        y_pred = exponential_decay(time_numeric, *popt)
        
        # Метрики качества
        r2 = r2_score(y_data, y_pred)
        rmse = np.sqrt(mean_squared_error(y_data, y_pred))
        
        return {
            'parameters': {'A': A_fit, 'tau': tau_fit, 'C': C_fit},
            'errors': {'A_error': errors[0], 'tau_error': errors[1], 'C_error': errors[2]},
            'metrics': {'R2': r2, 'RMSE': rmse},
            'predictions': y_pred,
            'time_numeric': time_numeric
        }
        
    except Exception as e:
        print(f"Ошибка при подгонке: {e}")
        return None

# Визуализация результатов
def plot_fit_results(df, fit_results, sensor_name):
    plt.figure(figsize=(12, 8))
    
    # Исходные данные
    plt.plot(df['timestamp'], df['value'], 'bo-', 
             alpha=0.7, label='Исходные данные', markersize=4)
    
    # Подобранная кривая
    plt.plot(df['timestamp'], fit_results['predictions'], 'r-', 
             linewidth=2, label='Экспоненциальная модель')
    
    # Асимптота
    C = fit_results['parameters']['C']
    plt.axhline(y=C, color='g', linestyle='--', 
                label=f'Асимптота: y = {C:.3f}')
    
    plt.title(f'Экспоненциальное затухание: {sensor_name}\n'
              f'$y = {fit_results["parameters"]["A"]:.3f} \\cdot e^{{-t/{fit_results["parameters"]["tau"]:.3f}}} + {fit_results["parameters"]["C"]:.3f}$\n'
              f'$R^2 = {fit_results["metrics"]["R2"]:.4f}$, RMSE = {fit_results["metrics"]["RMSE"]:.4f}')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Основная программа
if __name__ == "__main__":
    # Чтение данных (используем ваш формат)
    filename = '../data/beam/misc/2025-06-30.csv'
    df = pd.read_csv(filename, sep=';', header=None, 
                     names=['sensor_name', 'timestamp', 'value'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['value'] = df['value'].astype(float)
    
    # Подгонка экспоненты
    fit_results = fit_exponential_decay(df)
    
    if fit_results:
        # Вывод результатов
        print("="*50)
        print("РЕЗУЛЬТАТЫ ПОДГОНКИ ЭКСПОНЕНЦИАЛЬНОГО ЗАТУХАНИЯ")
        print("="*50)
        print(f"Параметры модели:")
        print(f"  A (амплитуда) = {fit_results['parameters']['A']:.6f} ± {fit_results['errors']['A_error']:.6f}")
        print(f"  τ (постоянная времени) = {fit_results['parameters']['tau']:.6f} ± {fit_results['errors']['tau_error']:.6f}")
        print(f"  C (смещение) = {fit_results['parameters']['C']:.6f} ± {fit_results['errors']['C_error']:.6f}")
        print(f"\nМетрики качества:")
        print(f"  R² = {fit_results['metrics']['R2']:.6f}")
        print(f"  RMSE = {fit_results['metrics']['RMSE']:.6f}")
        print(f"\nУравнение модели:")
        print(f"  y = {fit_results['parameters']['A']:.3f} * exp(-t/{fit_results['parameters']['tau']:.3f}) + {fit_results['parameters']['C']:.3f}")
        
        # Визуализация
        plot_fit_results(df, fit_results, df['sensor_name'].iloc[0])