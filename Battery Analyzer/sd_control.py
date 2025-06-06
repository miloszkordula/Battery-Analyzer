from machine import Pin, I2C, SPI, sleep, ADC, freq  # type: ignore
import os
import sdcard
import discharge_control
import errno
import gc

# SPI configuration for SD card and ADS1256
#spi = SPI(1, baudrate=500_000, polarity=0, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
spi = SPI(2, baudrate=5_000_000, polarity=0, phase=0, sck=Pin(47), mosi=Pin(18), miso=Pin(21))
sd_cs = Pin(38, Pin.OUT, value = 0)
#sd_cs = Pin(39, Pin.OUT, value = 0)

class Buffer:
    def __init__(self, buffersize, filename):
        self.buffersize: int = buffersize
        self.buffer: str[buffersize]
        self.filename: str = filename


def memory_monitor():  
    free_mem = gc.mem_free()
    used_mem = gc.mem_alloc()
    total_mem = free_mem + used_mem

    print("MEM Free: ", free_mem, " Used: ", used_mem, " Heap: ", total_mem)



# Function to initialize SD card
def initialize_sd_card():
    try:
        sd = sdcard.SDCard(spi, sd_cs)
        vfs = os.VfsFat(sd)
        os.mount(vfs, "/sd")
        print("SD card mounted at /sd")

        # ==== Print SD card info ====
        statvfs = os.statvfs("/sd")

        block_size = statvfs[0]      # Usually 512 bytes
        total_blocks = statvfs[2]    # Total number of blocks
        free_blocks = statvfs[3]     # Free blocks

        total_size = (total_blocks * block_size) / (1024 * 1024)
        free_size = (free_blocks * block_size) / (1024 * 1024)

        print(f"Total size: {total_size:.2f} MB")
        print(f"Free space: {free_size:.2f} MB")

        # ==== List contents ====
        print("SD Root directory contents:")
        print(os.listdir("/sd"))

    except OSError as e:
        if e.args and e.args[0] == errno.ENOENT:
            print("SD No such file or directory — SD card not found or miswired")
        elif e.args and e.args[0] == errno.EIO:
            print("SD I/O error — possible wiring or card problem")
        else:
            print("SD card error:", e)

def log_to_sd(filename):
    global discharge_control
    try:
        with open("/sd/" + filename, "a") as f:
            for line in discharge_control.global_buffer:
                f.write(line)
            f.close()
        memory_monitor()
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
