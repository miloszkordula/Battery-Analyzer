import numpy as np
from scipy.optimize import curve_fit



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
