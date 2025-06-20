import plotly.graph_objects as go
import numpy as np

def input_plot(t_seg, v_seg, i_seg, f):
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
        title='Input plot for ' + str(f) + 'Hz',
        xaxis=dict(title='Time [s]'),
        yaxis=dict(
            title='Voltage [V]',
        ),
        yaxis2=dict(
            title='Current [A]',
            tickfont=dict(color='orange'),
            overlaying='y',
            side='right'
        ),
        showlegend=True,
        dragmode='zoom'
    )
    # Show the plot
    fig.show()


def fourier_plot(freqs_fft, V_fft, I_fft, f_target):
    """
    Plot magnitude spectra of voltage and current FFTs using Plotly.

    Parameters:
        freqs_fft (np.ndarray): Array of FFT frequencies.
        V_fft (np.ndarray): FFT of the voltage signal.
        I_fft (np.ndarray): FFT of the current signal.
        f_target (float): Target frequency to highlight.
    """

    # Compute magnitude spectra
    V_mag = np.abs(V_fft)
    I_mag = np.abs(I_fft)

    # Only keep positive frequencies
    mask = freqs_fft >= 0
    freqs_plot = freqs_fft[mask]
    V_mag_plot = V_mag[mask]
    I_mag_plot = I_mag[mask]

    # Create traces
    voltage_trace = go.Scatter(x=freqs_plot, y=V_mag_plot, mode='lines+markers', name='|V_fft|')
    current_trace = go.Scatter(x=freqs_plot, y=I_mag_plot, mode='lines+markers', name='|I_fft|')
    target_line = go.Scatter(
        x=[f_target, f_target],
        y=[0, max(max(V_mag_plot), max(I_mag_plot))],
        mode='lines',
        name='Target f',
        line=dict(dash='dash', color='red')
    )

    # Create layout
    layout = go.Layout(
        title='FFT Magnitude Spectrum',
        xaxis=dict(title='Frequency [Hz]'),
        yaxis=dict(title='Magnitude'),
        legend=dict(x=0.01, y=0.99)
    )

    # Plot
    fig = go.Figure(data=[voltage_trace, current_trace, target_line], layout=layout)
    fig.show()


def nyquilist_plot(Z, fitted_impedance, iteration, first_energy):
        fig = go.Figure()
        # Add the measured data
        fig.add_trace(go.Scatter(x=Z.real, y=-Z.imag, mode='lines+markers', name='Measured Data'))
        # Add the fitted impedance
        fig.add_trace(go.Scatter(x=fitted_impedance.real, y=-fitted_impedance.imag, mode='lines+markers', name='Fitted Circuit'))

        fig.update_layout(
            title='Nyquist Plot No. ' + str(int(iteration)) + ' Discharged before: ' + str(int(first_energy*1000)/1000)+ 'mAh',
            xaxis_title='Re(Z) [Ohms]',
            yaxis_title='-Im(Z) [Ohms]',
            showlegend=True,
            dragmode='zoom' 
        )
        # Show the plot
        

        fig.show()


def output_plot(E_list, Vo_list, R_s_list, R_p_list, C_p_list):
    fig = go.Figure()

    # Trace 1 - Open Circuit Voltage
    fig.add_trace(go.Scatter(
        y=Vo_list, x=E_list, mode='lines+markers', name='Open Circuit Voltage [V]', 
        yaxis='y'
    ))

    # Trace 2 - Electrolyte Resistance
    fig.add_trace(go.Scatter(
        y=R_s_list, x=E_list, mode='lines+markers', name='Electrolyte Resistance [Ohm]', 
        yaxis='y2'
    ))

    # Trace 3 - Charge Transfer Resistance
    fig.add_trace(go.Scatter(
        y=R_p_list, x=E_list, mode='lines+markers', name='Charge Transfer Resistance [Ohm]', 
        yaxis='y2'
    ))

    # Trace 4 - Charge Transfer Capacitance
    fig.add_trace(go.Scatter(
        y=C_p_list, x=E_list, mode='lines+markers', name='Charge Transfer Capacitance [F]', 
        yaxis='y4'
    ))

    # Update layout with multiple y-axes
    fig.update_layout(
        title='Battery parameters over discharged capacity',
        xaxis=dict(title='Discharged [mAh]'),

        yaxis=dict(
            title='Open Circuit Voltage [V]',
        ),

        yaxis2=dict(
            title='Resistance [Ohm]',
            overlaying='y',
            side='left',
            position=0.1
        ),

        yaxis4=dict(
            title='Charge Transfer Capacitance [F]',
            anchor='free',
            overlaying='y',
            side='right',
            position=0.95
        ),

        showlegend=True,
        dragmode='zoom'
    )

    fig.show()



