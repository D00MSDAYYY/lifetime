import numpy as np


def moving_average(signal, window_size=5):
    """Сглаживание спектра скользящим средним."""
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(signal, window, mode='same')
    return smoothed
