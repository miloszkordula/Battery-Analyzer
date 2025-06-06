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
    status_lines = [
        f"V: {discharge_control.global_last_voltage/10_000:.3f}mV",
        f"I: {discharge_control.global_last_current/10_000:.3f}mA",
        f"t: {int(extended_ticks_us.global_time_tracker.ticks_us()/60_000_000)}m {(extended_ticks_us.global_time_tracker.ticks_us()/1_000_000)%60:.2f}s",
        f"f: {discharge_control.global_filename}",
        f"l: {discharge_control.global_loop_iteration} f: {discharge_control.global_freq:.3f}",
        f"E: {float(discharge_control.global_energy)/1_000_000_000:.3f}mAh"
    ]
    display_status(status_lines)

def display_task_if_active():
    print("DP Display task init")
    time.sleep(10)
    while discharge_control.global_is_in_progress == 0:
        print("DP Task not started yet")
        time.sleep(1)
    while discharge_control.global_is_in_progress == 1:
        display_disharge_status()
        time.sleep(0.1)
    print("DP Display task ended")



