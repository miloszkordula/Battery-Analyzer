import io_control
import time
from sh1106 import SH1106_I2C
import discharge_control
import extended_ticks_us

# OLED initialization
WIDTH = 128
HEIGHT = 64
oled = SH1106_I2C(WIDTH, HEIGHT, io_control.i2c, rotate=False)
oled.rotate(180)

# Function to display status on OLED
def display_status(status_lines):
    oled.fill(0)  # Clear the screen
    for i, line in enumerate(status_lines):
        oled.text(line, 0, i * 10)  # Display each line
    oled.show()



def display_disharge_status():
    voltage, measured_current = io_control.ads1256.get_reading_ADS1256()
    status_lines = [
        #f"V: {io_control.get_voltage():.1f}mV",
        #f"I: {io_control.get_current():.2f}mA",
        f"V: {voltage:.1f}mV",
        f"I: {measured_current:.2f}mA",
        f"t: {int(extended_ticks_us.global_time_tracker.ticks_us()/60_000_000)}m {(extended_ticks_us.global_time_tracker.ticks_us()/1_000_000)%60:.2f}s",
        f"f: {discharge_control.global_filename}",
        f"loop: {discharge_control.global_loop_iteration}",
        f"E: {float(discharge_control.global_energy)/1_000_000_000:.3f}mAh"
    ]
    display_status(status_lines)

def display_task_if_active():
    print("DP Display task started")
    time.sleep(10)
    while discharge_control.global_is_in_progress == 0:
        print("DP Task not started yet")
        time.sleep(1)
    while discharge_control.global_is_in_progress == 1:
        display_disharge_status()
        time.sleep(0.2)
    print("DP Display task ended")



