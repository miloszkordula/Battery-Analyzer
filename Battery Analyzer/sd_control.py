from machine import Pin, I2C, SPI, sleep, ADC, freq  # type: ignore
import os
import sdcard
import discharge_control

# SPI configuration for SD card and ADS1256
#spi = SPI(1, baudrate=500_000, polarity=0, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
#spi = SPI(1, baudrate=500_000, polarity=0, phase=1, sck=Pin(35), mosi=Pin(36), miso=Pin(37))
sd_cs = Pin(38, Pin.OUT)

class Buffer:
    def __init__(self, buffersize, filename):
        self.buffersize: int = buffersize
        self.buffer: str[buffersize]
        self.filename: str = filename


# Function to initialize SD card
def initialize_sd_card():
    try:
        #sd = sdcard.SDCard(spi, sd_cs)  # Initialize SD card
       # vfs = os.VfsFat(sd)
       # os.mount(vfs, "/sd")
        print("SD Card init OK")
        return "SD Card OK"
    except Exception as e:
        print("SD Card init Error")
        return f"SD Error: {str(e)}"

def log_to_sd(filename):
    global discharge_control
    try:
        with open("/sd/" + filename, "a") as f:
            for line in discharge_control.global_buffer:
                f.write(line)
            f.close()
        discharge_control.global_buffer.clear()
    except Exception as e:
        print(f"SD Error saving file to card: {e}")
        discharge_control.global_buffer.clear()

def get_new_filename():
    try:
        existing_files = os.listdir("/sd/")
        print(f"SD Found SD card filesystem")
        index = 1
        while True:
            filename = f"{index:06d}.txt"
            if filename not in existing_files:
                print(f"SD Got new filname")
                return filename
            index += 1
            print(f"SD Filename: {filename} exist")
    except Exception as e:
        print(f"SD Error cannot get filename: {e}")
