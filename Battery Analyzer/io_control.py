from machine import Pin, I2C, SPI, sleep, ADC, freq # type: ignore
import ext_lib.mcp4725 as mcp4725
from lib.ads1256lib import ADS1256

resistance = 7.8 #[Ohm]
DAC_coefficient = (4095*resistance)/3300

ADC_input_voltage_coefficient = 2.5  * 4076 / 0x7FFFFF
ADC_current_feedback_coefficient = 2.5  * 3968 / (0x7FFFFF*resistance)

# I2C configuration
i2c = I2C(0, scl=Pin(4), sda=Pin(5), freq=400000)

# create the MCP4725 driver
dac=mcp4725.MCP4725(i2c)

# Pin definitions
DRDY = Pin(11, Pin.IN)
CS = Pin(10, Pin.OUT, value = 0)
SYNC = Pin(9, Pin.OUT, value = 1)

# SPI setup (slow speed for stability)
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=1, sck=Pin(14), mosi=Pin(13), miso=Pin(12))

ads1256 = ADS1256(spi, CS, DRDY, SYNC,
                   ADC_input_voltage_coefficient, ADC_current_feedback_coefficient)

def scan_i2c():
    print('I2C Scan i2c bus...')
    devices = i2c.scan()

    if len(devices) == 0:
        print("I2C No i2c device !")
    else:
        print('I2C i2c devices found:',len(devices))

    for device in devices:  
        print("Decimal address: ",device," | Hexa address: ",hex(device))

# Function to set current on load [mA], step 0.052[mA], range 0-211.5[mA]
def set_current(current):
    dac.write(int(current*DAC_coefficient))
