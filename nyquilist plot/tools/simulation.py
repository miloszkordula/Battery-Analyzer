import numpy as np
import plotly.graph_objs as go

# Parametry modelu
Rs = 0.02        # Ohm
Rct = 0.05       # Ohm
Cdl = 0.2        # Farad
sigma = 0.1      # Ohm·s^(-0.5)

frequencies = np.logspace(9, 0, num=100)  # Hz
omega = 2 * np.pi * frequencies             # rad/s

# Obliczenia impedancji
Z_cdl = 1 / (1j * omega * Cdl)
Z_warburg = sigma * (1 - 1j) / np.sqrt(omega)
Z_parallel = 1 / (1/Rct + 1/Z_cdl)
Z_total = Rs + Z_parallel + Z_warburg

# Re/Im
Z_real = np.real(Z_total)
Z_imag = -np.imag(Z_total)
# Wykres Nyquista
fig = go.Figure()
fig.add_trace(go.Scatter(x=Z_real, y=Z_imag, mode='lines+markers', name='Krzywa Nyquista'))

fig.update_layout(
    title="Wykres Nyquista – R0 + (Rct || Cct) + Warburg",
    xaxis_title="Re(Z) [Ω]",
    yaxis_title="-Im(Z) [Ω]"
)

fig.show()
