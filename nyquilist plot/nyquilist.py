import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt, resample
from scipy.optimize import curve_fit

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
    new_time = np.linspace(time.min(), time.max(), len(time))
    voltage = np.interp(new_time, time, voltage)
    current = np.interp(new_time, time, current)

    # Remove DC offset
    #voltage -= 3.031
    #current -= np.mean(current)

    return new_time, voltage, current, sample_rate



def time_to_frequency(time, signal):
    """Convert time-domain signal to frequency domain using FFT."""
    dt = time[1] - time[0]
    N = len(time)

    #signal = signal - np.mean(signal)

    # Apply Hann window to reduce spectral leakage
    window = np.hanning(N)
    signal_windowed = signal * window

    freq = fftfreq(N, dt)
    #S_f = fft(signal_windowed)
    S_f = fft(signal_windowed)/ N

    positive_idx = freq > 0.1
    #print(freq[positive_idx], S_f[positive_idx])
    return freq[positive_idx], S_f[positive_idx]

def equivalent_circuit_fit(frequency, impedance):
    """Fit impedance to Rs + 1/(1/Rp + jωCp)."""
    def circuit_model(freq, R_s, R_p, C_p):
        omega = 2 * np.pi * freq
        Z_parallel = 1 / (1/R_p + 1j * omega * C_p)
        return R_s + Z_parallel

    def real_part(freq, R_s, R_p, C_p):
        return circuit_model(freq, R_s, R_p, C_p).real

    def imag_part(freq, R_s, R_p, C_p):
        return circuit_model(freq, R_s, R_p, C_p).imag

    Z_real = impedance.real
    Z_imag = impedance.imag

    popt_real, _ = curve_fit(real_part, frequency, Z_real, p0=[1, 1, 1e-6])
    popt_imag, _ = curve_fit(imag_part, frequency, Z_imag, p0=[1, 1, 1e-6])

    R_s, R_p, C_p = (popt_real + popt_imag) / 2
    return R_s, R_p, C_p

def low_pass_filter(signal, cutoff_freq, sample_rate, order=4):
    nyquist = 0.5 * sample_rate
    normal_cutoff = min(cutoff_freq / nyquist, 0.99)
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, signal)


def make_nyquist_plot(filename):
    time, current, voltage = load_data(filename)
    dt = np.mean(np.diff(time))  # Sampling interval

    #mask = (time > 42.2) & (time < 49)
    #time = time[mask]
    #current = current[mask]
    #voltage = voltage[mask]

    current -= np.mean(current)
    voltage -= np.mean(voltage)
    window = np.hanning(len(current))
    current_windowed = current * window
    voltage_windowed = voltage * window

    # FFT
    I_fft = fft(current_windowed)
    V_fft = fft(voltage_windowed)
    freqs = fftfreq(len(time), d=dt)

    # Impedance Z = V / I
    Z = V_fft / I_fft

    # Use only positive frequencies
    pos_mask = freqs > 0
    Z_real = Z[pos_mask].real
    Z_imag = Z[pos_mask].imag

    fig = go.Figure()

    # Fit circuit model
    R_s, R_p, C_p = equivalent_circuit_fit(freqs, Z)
    print(f"Fitted Circuit Parameters:\nR_s = {R_s:.2f} Ω, R_p = {R_p:.2f} Ω, C_p = {C_p:.2e} F")
    fitted_impedance = R_s + 1 / (1/R_p + 1j * 2 * np.pi * freqs * C_p)
    
    #for x in impedance: x*1000*1000j
    fig = go.Figure()
    # Add the measured data
    fig.add_trace(go.Scatter(x=Z_real, y=-Z_imag, mode='markers', name='Measured Data'))
    # Add the fitted impedance
    fig.add_trace(go.Scatter(x=fitted_impedance.real, y=fitted_impedance.imag, mode='lines', name='Fitted Circuit'))
    # Customize the layout
    fig.update_layout(
        title='Nyquist Plot',
        xaxis_title='Re(Z) [Ohms]',
        yaxis_title='-Im(Z) [Ohms]',
        template='plotly_dark',  # You can change the theme here
        showlegend=True,
        dragmode='zoom'  # Enable zoom interaction
    )
    # Show the plot
    fig.show()

def load_data_single_freq(filename):
    data = np.loadtxt(filename, delimiter=',')
    time = data[:, 0] * 1e-3  # ms → s
    current = data[:, 2] * 1e-3  # mA → A
    voltage = data[:, 3] * 1e-3  # mV → V
    freq = data[:, 4]  # Hz
    return time, current, voltage, freq

def extract_impedance_points(time, current, voltage, freq):
    Z_list = []
    freq_list = []

    unique_freqs = np.unique(freq)
    for f in unique_freqs:
        # Mask rows for this frequency
        mask = freq == f
        indices = np.where(mask)[0]

        # Exclude first and last row
        if len(indices) <= 101:
            continue
        idx_range = indices[100:-1]

        t_seg = time[idx_range]
        i_seg = current[idx_range] - np.mean(current[idx_range])
        v_seg = - voltage[idx_range] + 2.83

        fig = go.Figure()
        # Add the measured data

        # First trace - voltage (left y-axis)
        fig.add_trace(go.Scatter(
            x=t_seg,
            y=v_seg,
            mode='markers',
            name='Voltage',
            yaxis='y1'
        ))

        # Second trace - current (right y-axis)
        fig.add_trace(go.Scatter(
            x=t_seg,
            y=i_seg,
            mode='markers',
            name='Current',
            marker=dict(color='orange'),
            yaxis='y2'
        ))
            # Update layout to add a second y-axis
        fig.update_layout(
            title='Nyquist Plot',
            xaxis=dict(title='Time'),
            yaxis=dict(
                title='Voltage',
                #titlefont=dict(color='blue'),
                tickfont=dict(color='blue')
            ),
            yaxis2=dict(
                title='Current',
                #titlefont=dict(color='orange'),
                tickfont=dict(color='orange'),
                overlaying='y',
                side='right'
            ),
            template='plotly_dark',
            showlegend=True,
            dragmode='zoom'
        )
        # Show the plot
        #fig.show()


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



    return np.array(Z_list), np.array(freq_list)



def main():
    filename = "data20.txt"

    time, current, voltage, freq = load_data_single_freq(filename)
    Z, f = extract_impedance_points(time, current, voltage, freq)

    # Fit circuit model
    #R_s, R_p, C_p = equivalent_circuit_fit(f, Z)
    #print(f"Fitted Circuit Parameters:\nR_s = {R_s:.2f} Ω, R_p = {R_p:.2f} Ω, C_p = {C_p:.2e} F")
    #fitted_impedance = R_s + 1 / (1/R_p + 1j * 2 * np.pi * f * C_p)

    fig = go.Figure()
    # Add the measured data
    fig.add_trace(go.Scatter(x=Z.real, y=-Z.imag, mode='markers', name='Measured Data'))
    # Add the fitted impedance
    #fig.add_trace(go.Scatter(x=fitted_impedance.real, y=fitted_impedance.imag, mode='lines', name='Fitted Circuit'))
    # Customize the layout
    fig.update_layout(
        title='Nyquist Plot',
        xaxis_title='Re(Z) [Ohms]',
        yaxis_title='-Im(Z) [Ohms]',
        template='plotly_dark',  # You can change the theme here
        showlegend=True,
        dragmode='zoom'  # Enable zoom interaction
    )
    # Show the plot
    fig.show()




    
    # Load and preprocess data
    time, current, voltage = load_data(filename)
    time, voltage, current, sample_rate = preprocess_data(time, voltage, current)

    voltage = low_pass_filter(voltage, cutoff_freq=100, sample_rate=sample_rate)
    current = low_pass_filter(current, cutoff_freq=100, sample_rate=sample_rate)


    fig = go.Figure()
    # Add the measured data

    # First trace - voltage (left y-axis)
    fig.add_trace(go.Scatter(
        x=time,
        y=voltage,
        mode='markers',
        name='Voltage',
        yaxis='y1'
    ))

    # Second trace - current (right y-axis)
    fig.add_trace(go.Scatter(
        x=time,
        y=current,
        mode='markers',
        name='Current',
        marker=dict(color='orange'),
        yaxis='y2'
    ))

    # Update layout to add a second y-axis
    fig.update_layout(
        title='Nyquist Plot',
        xaxis=dict(title='Time'),
        yaxis=dict(
            title='Voltage',
            #titlefont=dict(color='blue'),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title='Current',
            #titlefont=dict(color='orange'),
            tickfont=dict(color='orange'),
            overlaying='y',
            side='right'
        ),
        template='plotly_dark',
        showlegend=True,
        dragmode='zoom'
    )
    # Show the plot
    fig.show()

    resistance = []

    # Transform to frequency domain
    alg_type = 4    #best no.2

    if alg_type == 1:
        for i, x in enumerate(voltage):
            resistance.append((voltage[0] - x) / (current[i]))
        frequency, impedance = time_to_frequency(time, resistance)
    
    if alg_type == 2:
        for x in voltage:
            resistance = (voltage[0] - x) / current
        frequency, impedance = time_to_frequency(time, resistance)

    if alg_type == 3:
        resistance = voltage / current
        frequency, impedance = time_to_frequency(time, resistance)

    if alg_type == 4: 
        frequency, V_f = time_to_frequency(time, voltage)
        _, I_f = time_to_frequency(time, current)  # FFT of current
        impedance = V_f / I_f # Prevent division errors



    #for x in resistance: print(x)

    
    fig = go.Figure()

    # Add the measured data
    fig.add_trace(go.Scatter(x=time, y=resistance, mode='markers', name='Measured Data'))
    # Customize the layout
    fig.update_layout(
        title='Nyquist Plot',
        xaxis_title='time',
        yaxis_title='resistance',
        template='plotly_dark',  # You can change the theme here
        showlegend=True,
        dragmode='zoom'  # Enable zoom interaction
    )
    # Show the plot
    # fig.show()



    # Fit circuit model
    #R_s, R_p, C_p = equivalent_circuit_fit(frequency, impedance)
   # print(f"Fitted Circuit Parameters:\nR_s = {R_s:.2f} Ω, R_p = {R_p:.2f} Ω, C_p = {C_p:.2e} F")
    #fitted_impedance = R_s + 1 / (1/R_p + 1j * 2 * np.pi * frequency * C_p)
    
    #for x in impedance: x*1000*1000j
    fig = go.Figure()
    # Add the measured data
    fig.add_trace(go.Scatter(x=impedance.real, y=-impedance.imag, mode='markers', name='Measured Data'))
    # Add the fitted impedance
    #fig.add_trace(go.Scatter(x=fitted_impedance.real, y=fitted_impedance.imag, mode='lines', name='Fitted Circuit'))
    # Customize the layout
    fig.update_layout(
        title='Nyquist Plot',
        xaxis_title='Re(Z) [Ohms]',
        yaxis_title='Im(Z) [Ohms]',
        template='plotly_dark',  # You can change the theme here
        showlegend=True,
        dragmode='zoom'  # Enable zoom interaction
    )
    # Show the plot
    fig.show()

    make_nyquist_plot(filename)


main()
