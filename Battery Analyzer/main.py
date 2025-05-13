from machine import Pin, I2C, SPI, sleep, ADC, freq  # type: ignore
import _thread
import test
import io_control
import display
import discharge_control
import sd_control


### Setings ###
l_time = 30_000_000
l_current = 0

h_time = 30_000_000
h_current = 100

repetitions = 60

log_downsample = 10 #Co który "nudny" log ma być  zapisany

eis_current = 10 #mA
min_freq = 0.2 #Hz
max_freq = 200 #Hz
###############


# Main code
try:
    # Test devices
    print("#####################################")
    print(f"CPU Freq: {freq()/1_000_000}MHz")
    test.scan_i2c()
    sd_status = sd_control.initialize_sd_card()


    _thread.start_new_thread(display.display_task_if_active, ())
    discharge_control.discharge_program(l_time, l_current, h_time, h_current, eis_current, min_freq, max_freq, repetitions, log_downsample)

    # Display on OLED
    while True:
        #ina_status, voltage_m_time = test_ina219()
        io_control.set_current(0)
        display.display_status(["Discharge","Finnished",f"E: {float(discharge_control.global_energy)/1_000_000_000:.3f}mAh"])
        

except Exception as e:
    # Display error message
    print(e)
    display.display_status(["Init Error:", str(e)[:16], str(e[16:32])])