import numpy as np
from scipy.signal import butter, filtfilt, resample


def load_data(filename):
    """Load data from text file: timestamp (us), current (mA), voltage (mV)."""
    skip_row = 100
    data = np.loadtxt(filename, delimiter=',', skiprows=0)

    timestamps = data[:, 0] * 1e-3  # Convert miliseconds to seconds
    current = data[:, 2] * 1e-3  # Convert mA to A
    voltage = data[:, 3] * 1e-3  # Convert mV to V

    return timestamps, current, voltage

def preprocess_data(time, voltage, current):
    """Interpolates data for uniform sampling and removes DC offset."""
    # Ensure uniform sampling
    sample_rate = 1 / np.mean(np.diff(time))  # Approximate sampling rate
    new_time = np.linspace(time.min(), time.max(), int(len(time)))
    voltage = np.interp(new_time, time, voltage)
    current = np.interp(new_time, time, current)

    # Remove DC offset
    #voltage -= 3.031
    #current -= np.mean(current)

    return new_time, voltage, current, sample_rate


def low_pass_filter(signal, cutoff_freq, sample_rate, order=2):
    nyquist = 0.5 * sample_rate
    normal_cutoff = min(cutoff_freq / nyquist, 0.99)
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, signal)
