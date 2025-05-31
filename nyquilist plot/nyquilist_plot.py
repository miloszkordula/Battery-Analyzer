import numpy as np
import plotly.graph_objects as go
from scipy.fft import fft, fftfreq
from preprocess import load_data
from equivalent_circuit import equivalent_circuit_fit


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