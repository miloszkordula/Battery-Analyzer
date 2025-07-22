# Battery-Analyzer

The aim of this project was to design, build, and functionally validate a prototype of a low-cost system for discharging and advanced diagnostics of lithium batteries. The developed solution integrates:

# 1. Embedded hardware 
Digitally controlled electronic load (max 420 mA, 0–6 V), a precise 24-bit ADC ADS1256, a programmable 12-bit current source with an MCP4725 DAC and a complete measurement interface based on the ESP32-S3 microcontroller.

# 2. Embedded firmware 
MicroPython application implementing constant current discharge and electrochemical impedance spectroscopy (EIS) in the 0.05–50 Hz range, with data storage on a microSD card and visualization of current parameters on an OLED display.

# 3. Analytical software
Desktop Python package (NumPy/SciPy/Plotly) that automates signal filtering, FFT, Nyquist characteristic calculation, and Rₛ–(Rct||Cct) model fitting. Results on various stages can be presented as interactive graphs.

 
