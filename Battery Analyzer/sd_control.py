from machine import Pin, I2C, SPI, sleep, ADC, freq  # type: ignore
import os
import ext_lib.sdcard as sdcard
import errno
import gc
from struct import pack_into, unpack_from
import sys

# SPI configuration for SD card and ADS1256
spi = SPI(2, baudrate=5_000_000, polarity=0, phase=0, sck=Pin(47), mosi=Pin(18), miso=Pin(21))
sd_cs = Pin(38, Pin.OUT, value = 0)

global_buffer_size = 8000 # Ustawienie rozmiaru bufora
global_buffer_record_size = 34 # 2×int64 + 4×int32 + uint16
global_buffer = bytearray(global_buffer_size * global_buffer_record_size)
global_current_index = int(0)

def store_record(time_us, current, last_current, last_voltage, freq, energy_pAh, loop_iteration):
    global global_buffer, global_current_index
    offset = global_current_index * 34
    # Scale floats to fixed-point integers
    # Example: 1000 * volts, 1000 * amps
    pack_into('<qiiiiqH', global_buffer, offset,    # q = int64, i = int32
              int(time_us),                         # us     int64 max 290 000 years           
              int(current * 1000),                  # uA     int32 max 2147 A
              int(last_current),                    # 0.1uA  int32 max 214 A
              int(last_voltage),                    # 0.1uV  int32 max 214 V
              int(freq * 1_000_000),                # uHz    int32 max 2147 Hz
              int(energy_pAh),                      # pAh    int64 max 9 MAh
              int(loop_iteration))                  # No.   uint16 max 65000
    global_current_index = global_current_index + 1


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
        sys.path.append('/sd')

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
    global global_buffer, global_current_index
    try:
        with open("/sd/" + filename, "a") as f:
            for i in range(global_current_index):
                offset = i * 34
                time_us, current, last_current, last_voltage, freq, energy, loop = \
                    unpack_from('<qiiiiqH', global_buffer, offset)

                # Format line with fixed-point scaling restored
                line = "{:.3f}, {:.3f}, {:.4f}, {:.4f}, {:.6f}, {:.6f}, {}\n".format(
                    time_us / 1_000,                    # ms
                    current / 1000,                     # mA
                    last_current / 10000,               # mA
                    last_voltage / 10000,               # mV
                    freq / 1_000_000,                   # Hz
                    energy / 1_000_000_000,             # mAh
                    loop                                # No.
                )
                f.write(line)
        memory_monitor()
        global_current_index = 0
    except Exception as e:
        print(f"SD Error saving file to card: {e}")
        global_current_index = 0

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
