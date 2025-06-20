import numpy as np
from scipy.fft import fft, fftfreq
from preprocess import preprocess_data, low_pass_filter
from equivalent_circuit import equivalent_circuit_fit
from plots import input_plot



def extract_impedance_points(time, current, voltage, freq, energy, iteration, it, showInputPlot):
    Z_list = []
    freq_list = []

    iteration_mask = iteration == it
    iteration_indices = np.where(iteration_mask)[0]
    time = time[iteration_indices]
    current = current[iteration_indices]
    voltage = voltage[iteration_indices]
    freq = freq[iteration_indices]
    energy = energy[iteration_indices]

    
    Vo_mask = freq == 0
    Vo_indices = np.where(Vo_mask)[0]
    Vo_current = current[Vo_indices]
    Vo_voltage = voltage[Vo_indices]
    Vo = 0
    for i, Vo_I in enumerate(Vo_current):
        V_list = []
        if Vo_I < 0.005:
            V_list.append(Vo_voltage[i])
        if len(V_list):
            Vo = sum(V_list)/len(V_list)

    unique_freqs = np.unique(freq)
    for f in unique_freqs:

        if f > 0:

            # Mask rows for this frequency
            mask = freq == f
            indices = np.where(mask)[0]

            # Exclude first and last rows
            if len(indices) <= 30:
                continue
            idx_range = indices[10:-1]

            t_seg = time[idx_range]
            i_seg = current[idx_range] - np.mean(current[idx_range])
            v_seg = - voltage[idx_range] + np.mean(voltage[idx_range])

            t_seg, v_seg, i_seg, sample_rate = preprocess_data(t_seg, v_seg, i_seg)

            v_seg = low_pass_filter(v_seg, cutoff_freq=10*f, sample_rate=sample_rate)
            i_seg = low_pass_filter(i_seg, cutoff_freq=10*f, sample_rate=sample_rate)

            if showInputPlot: input_plot(t_seg, v_seg, i_seg, f)
          
            # Window to reduce leakage
            window = np.hanning(len(t_seg))
            i_seg *= window
            v_seg *= window

            # FFT
            I_fft = fft(i_seg)
            V_fft = fft(v_seg)
            dt = np.mean(np.diff(t_seg))
            freqs_fft = fftfreq(len(t_seg), dt)

            # Get index of closest FFT bin to target frequency
            target_idx = np.argmin(np.abs(freqs_fft - f))
            Z = V_fft[target_idx] / I_fft[target_idx]

            Z_list.append(Z)
            freq_list.append(f)

    impedance = np.array(Z_list)

    freqs = np.array(freq_list)

    R_s, R_p, C_p = equivalent_circuit_fit(freqs, impedance)
    print(f"Fitted Circuit Parameters No.{int(it)}:\nVo = {Vo:.3f} V R_s = {R_s:.3f} Ω, R_p = {R_p:.3f} Ω, C_p = {C_p:.3e} F")


    fitted_impedance = R_s + 1 / (1/R_p + 1j * 2 * np.pi * freqs * C_p)

    return np.array(Z_list), fitted_impedance, energy[0], Vo, R_s, R_p, C_p
