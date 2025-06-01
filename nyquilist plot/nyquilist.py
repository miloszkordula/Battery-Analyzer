import numpy as np
import plotly.graph_objects as go
from scipy.fft import fft, fftfreq
from single_points import load_data_single_freq, extract_impedance_points
from preprocess import load_data, preprocess_data, low_pass_filter
from nyquilist_plot import make_nyquist_plot


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


def main():
    filename = "data/data29.txt"

    time, current, voltage, freq = load_data_single_freq(filename)
    Z, f, fitted_impedance = extract_impedance_points(time, current, voltage, freq)

    # Fit circuit model
    #R_s, R_p, C_p = equivalent_circuit_fit(f, Z)
    #print(f"Fitted Circuit Parameters:\nR_s = {R_s:.2f} Ω, R_p = {R_p:.2f} Ω, C_p = {C_p:.2e} F")
    #fitted_impedance = R_s + 1 / (1/R_p + 1j * 2 * np.pi * f * C_p)

    fig = go.Figure()
    # Add the measured data
    fig.add_trace(go.Scatter(x=Z.real, y=-Z.imag, mode='markers', name='Measured Data'))
    # Add the fitted impedance
    fig.add_trace(go.Scatter(x=fitted_impedance.real, y=-fitted_impedance.imag, mode='lines', name='Fitted Circuit'))
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


    """

    
    # Load and preprocess data
    time, current, voltage = load_data(filename)
    time, voltage, current, sample_rate = preprocess_data(time, voltage, current)

    voltage = low_pass_filter(voltage, cutoff_freq=50, sample_rate=sample_rate)
    current = low_pass_filter(current, cutoff_freq=50, sample_rate=sample_rate)


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
    alg_type = 2    #best no.2

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

    """
main()
