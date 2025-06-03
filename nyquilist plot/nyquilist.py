import numpy as np
import plotly.graph_objects as go
from single_points import load_data_single_freq, extract_impedance_points


def main():
    filename = "data/data27.txt"

    time, current, voltage, freq = load_data_single_freq(filename)
    Z, f, fitted_impedance = extract_impedance_points(time, current, voltage, freq)


    fig = go.Figure()
    # Add the measured data
    fig.add_trace(go.Scatter(x=Z.real, y=-Z.imag, mode='lines+markers', name='Measured Data'))
    # Add the fitted impedance
    fig.add_trace(go.Scatter(x=fitted_impedance.real, y=-fitted_impedance.imag, mode='lines+markers', name='Fitted Circuit'))
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


main()
