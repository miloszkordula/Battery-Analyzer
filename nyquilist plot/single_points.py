import numpy as np
import plotly.graph_objects as go
from scipy.fft import fft, fftfreq
from preprocess import preprocess_data, low_pass_filter
from equivalent_circuit import equivalent_circuit_fit, auto_fit_eis



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

       # if f > 10:
        #    continue

        # Mask rows for this frequency
        mask = freq == f
        indices = np.where(mask)[0]

        # Exclude first and last row
        if len(indices) <= 30:
            continue
        idx_range = indices[10:-1]

        t_seg = time[idx_range]
        i_seg = current[idx_range] - np.mean(current[idx_range])
        v_seg = - voltage[idx_range] + np.mean(voltage[idx_range])#+ voltage[0]

        t_seg, v_seg, i_seg, sample_rate = preprocess_data(t_seg, v_seg, i_seg)

        v_seg = low_pass_filter(v_seg, cutoff_freq=10*f, sample_rate=sample_rate)
        i_seg = low_pass_filter(i_seg, cutoff_freq=10*f, sample_rate=sample_rate)


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
            title='Nyquist Plot ' + str(f),
            xaxis=dict(title='Time'),
            yaxis=dict(
                title='Voltage',
                #titlefont=dict(color='blue'),
                tickfont=dict(color='white')
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

    impedance = np.array(Z_list)

    freqs = np.array(freq_list)

    R_s, R_p, C_p, _ = auto_fit_eis(freqs, impedance)
    print(f"Fitted Circuit Parameters:\nR_s = {R_s:.2f} Ω, R_p = {R_p:.2f} Ω, C_p = {C_p:.2e} F")
    fitted_impedance = R_s + 1 / (1/R_p + 1j * 2 * np.pi * freqs * C_p)

    return np.array(Z_list), np.array(freq_list), fitted_impedance
