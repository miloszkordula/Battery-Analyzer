import numpy as np
from scipy.signal import butter, filtfilt


def preprocess_data(time, voltage, current):
    # Ensure uniform sampling
    sample_rate = 1 / np.mean(np.diff(time))  # Approximate sampling rate
    new_time = np.linspace(time.min(), time.max(), int(len(time)))
    voltage = np.interp(new_time, time, voltage)
    current = np.interp(new_time, time, current)

    return new_time, voltage, current, sample_rate


def low_pass_filter(signal, cutoff_freq, sample_rate, order=2):
    nyquist = 0.5 * sample_rate
    normal_cutoff = min(cutoff_freq / nyquist, 0.99)
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, signal)


def load_data_single_freq(filename):
    data = np.loadtxt(filename, delimiter=',', skiprows = 2)
    time = data[:, 0] * 1e-3  # ms → s
    current = data[:, 2] * 1e-3  # mA → A
    voltage = data[:, 3] * 1e-3  # mV → V
    freq = data[:, 4]  # Hz
    energy = data[:, 5] # mAh
    iteration = data[:, 6]
    return time, current, voltage, freq, energy, iteration
