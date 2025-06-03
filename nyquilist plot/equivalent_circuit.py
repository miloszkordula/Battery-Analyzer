import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import curve_fit

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

    initial_guess = [0.1, 0.1, 1e-6]  # Tweak this based on your data scale
    bounds = ([0, 1e-1, 1e-6], [np.inf, np.inf, np.inf])

    result = least_squares(residuals, initial_guess, args=(freq, Z_meas), bounds=bounds)

    R_s, R_p, C_p = result.x
    return R_s, R_p, C_p


def sort_by_frequency(freqs, Z):
    idx = np.argsort(freqs)[::-1]  # High to low freq
    return np.array(freqs)[idx], np.array(Z)[idx]

def remove_duplicates_outliers(freqs, Z, z_threshold=5):
    from scipy.stats import zscore
    real_z = Z.real
    imag_z = Z.imag

    # Remove duplicates
    _, unique_idx = np.unique(freqs, return_index=True)

    # Z-score filter on magnitude
    Zmag = np.abs(Z[unique_idx])
    mask = np.abs(zscore(Zmag)) < z_threshold

    return freqs[unique_idx][mask], Z[unique_idx][mask]


def crop_cpe_tail(freqs, Z, max_phase_deg=-45):
    phase_angle = np.angle(Z, deg=True)
    idx = np.where(phase_angle > max_phase_deg)[0]  # Where phase becomes inductive (positive)
    if len(idx) == 0:
        return freqs, Z
    return freqs[:idx[0]], Z[:idx[0]]


def preprocess_impedance(freqs, Z):
    freqs, Z = sort_by_frequency(freqs, Z)
    freqs, Z = remove_duplicates_outliers(freqs, Z)
    #freqs, Z = crop_cpe_tail(freqs, Z, max_phase_deg=-60)
    return freqs, Z









# ----- STEP 1: CPE Detection -----
def detect_cpe_region(freqs, Z, phase_threshold_deg=-60):
    phase_angle = np.angle(Z, deg=True)
    idx = np.argsort(freqs)
    freqs = np.array(freqs)[idx]
    phase_angle = np.array(phase_angle)[idx]

    below_thresh = np.where(phase_angle < phase_threshold_deg)[0]
    if len(below_thresh) > 0:
        return True, freqs[below_thresh[0]]
    return False, None

# ----- STEP 2: Standard Rs + Rp || Cp -----
def standard_circuit_model(freqs, R_s, R_p, C_p):
    omega = 2 * np.pi * freqs
    Z_parallel = 1 / (1/R_p + 1j * omega * C_p)
    return R_s + Z_parallel

def fit_standard_circuit(freqs, Z):
    freqs_extended = np.logspace(-2, 6, 52)

    def real_part(freqs_extended, R_s, R_p, C_p):
        return standard_circuit_model(freqs_extended, R_s, R_p, C_p).real
    def imag_part(freqs_extended, R_s, R_p, C_p):
        return standard_circuit_model(freqs_extended, R_s, R_p, C_p).imag

    Z_real = Z.real
    Z_imag = Z.imag
    p0 = [0.2, 0.5, 1e-6]
    bounds = ([0.1, 0.1, 1e-9], [1, 1, 1e-1])
    popt_real, _ = curve_fit(real_part, freqs, Z_real, p0=p0, bounds=bounds)
    popt_imag, _ = curve_fit(imag_part, freqs, Z_imag, p0=p0, bounds=bounds)

    R_s, R_p, C_p = (popt_real + popt_imag) / 2

    return R_s, R_p, C_p

# ----- STEP 3: Rs + Rp || CPE -----
def cpe_circuit_model(freqs, R_s, R_p, Q, n):
    omega = 2 * np.pi * freqs
    Z_cpe = 1 / (Q * (1j * omega)**n)
    Z_parallel = 1 / (1/R_p + 1/Z_cpe)
    return R_s + Z_parallel

def fit_cpe_circuit(freqs, Z):
    def real_part(freqs, R_s, R_p, Q, n):
        return cpe_circuit_model(freqs, R_s, R_p, Q, n).real
    def imag_part(freqs, R_s, R_p, Q, n):
        return cpe_circuit_model(freqs, R_s, R_p, Q, n).imag

    Z_real = Z.real
    Z_imag = Z.imag
    p0 = [0.2, 0.5, 1e-4, 0.8]
    bounds = ([0, 1e-3, 1e-12, 0.3], [10, 100, 1e-2, 1.0])
    popt_real, _ = curve_fit(real_part, freqs, Z_real, p0=p0, bounds=bounds)
    popt_imag, _ = curve_fit(imag_part, freqs, Z_imag, p0=p0, bounds=bounds)

    R_s, R_p, C_p, n = (popt_real + popt_imag) / 2

    return R_s, R_p, C_p

# ----- STEP 4: Automatic Logic -----
def auto_fit_eis(freqs, Z):
    freqs, Z = preprocess_impedance(freqs, Z)

    cpe_present, cutoff_freq = detect_cpe_region(freqs, Z)
    freqs = np.array(freqs)
    Z = np.array(Z)

    if cpe_present:
        print(f"CPE-like behavior detected. Fitting CPE model.")
        R_s, R_p, C_p = fit_cpe_circuit(freqs, Z)
        return R_s, R_p, C_p, "cpe"
    else:
        print("No CPE behavior detected. Fitting standard model.")
        R_s, R_p, C_p = fit_standard_circuit(freqs, Z)
        return R_s, R_p, C_p, "standard"



