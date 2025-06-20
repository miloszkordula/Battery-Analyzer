import numpy as np
from scipy.optimize import least_squares

def equivalent_circuit_fit(frequency, impedance):
    """
    Fit impedance data to Rs + 1 / (1/Rp + jωCp)
    using least squares on complex values directly.
    """
    def circuit_model(freq, R_s, R_p, C_p):
        omega = 2 * np.pi * freq
        Z_parallel = 1 / (1/R_p + 1j * omega * C_p)
        return R_s + Z_parallel

    def residuals(params, freq, Z_meas):
        R_s, R_p, C_p = params
        Z_model = circuit_model(freq, R_s, R_p, C_p)
        return np.concatenate([
            (Z_model.real - Z_meas.real),
            (Z_model.imag - Z_meas.imag)
        ])

    freq = np.array(frequency)
    Z_meas = np.array(impedance)

    initial_guess = [0.1, 0.1, 1e-6]
    bounds = ([0, 1e-2, 1e-6], [np.inf, np.inf, np.inf])

    result = least_squares(residuals, initial_guess, args=(freq, Z_meas), bounds=bounds)

    R_s, R_p, C_p = result.x
    return R_s, R_p, C_p












