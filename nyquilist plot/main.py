import numpy as np
import os
from preprocess import load_data_single_freq
from single_points import extract_impedance_points
from plots import nyquilist_plot, output_plot


def main():

    filename = input("Enter path to file: ").strip()
    while not os.path.isfile(filename):
        print("File not found. Please try again.")

    showInputPlot = input("Show input plots? True/False: ").strip().lower() == "true"
    showFourierPlot = input("Show Fourier plots? True/False: ").strip().lower() == "true"
    showNyqulistPlot = input("Show Nyqulist plots? True/False: ").strip().lower() == "true"

    time, current, voltage, freq, energy, iterations = load_data_single_freq(filename)

    all_iterations  = np.unique(iterations)

    Vo_list ,R_s_list, R_p_list, C_p_list, E_list = [], [], [], [], []


    for iteration in all_iterations:

        if iteration > 18:
            continue

        Z, fitted_impedance, first_energy, Vo, R_s, R_p, C_p = extract_impedance_points(
            time, current, voltage, freq, energy, iterations, iteration, showInputPlot, showFourierPlot)

        Vo_list.append(Vo)
        R_s_list.append(R_s)
        R_p_list.append(R_p)
        C_p_list.append(C_p)
        E_list.append((first_energy*1000)/1000)

        if showNyqulistPlot: nyquilist_plot(Z, fitted_impedance, iteration, first_energy)

    output_plot(E_list, Vo_list, R_s_list, R_p_list, C_p_list)


if __name__ == "__main__":
    main()
