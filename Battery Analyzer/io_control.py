from machine import Pin, I2C, SPI, sleep, ADC, freq # type: ignore
import mcp4725
from ads1256lib import ADS1256
# ADC configuration
samples = 16

resistance = 15.6 #[Ohm]
DAC_coefficient = (4096*resistance*0.84)/3300

CH_current_feedback = 0x08 #CH0
CH_input_voltage = 0x18 #CH1

ADC_input_voltage_coefficient = 2.5  * 3410 / 0x7FFFFF
ADC_current_feedback_coefficient = 2.5  * 3410 / (0x7FFFFF*resistance)



adc = ADC(Pin(7))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

adc_current = ADC(Pin(15))
adc_current.atten(ADC.ATTN_11DB)
adc_current.width(ADC.WIDTH_12BIT)

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

def get_voltage():
    total = 0.0
    samples = 16  #2-bit (4^2) oversample
    for _ in range(samples):
        total += adc.read()
    average = total / samples
    return average * 3.9 / (4.095 * 0.774)

def get_current():
    total = 0.0
    samples = 16  #2-bit (4^2) oversample
    for _ in range(samples):
        total += adc_current.read()
    average = total / samples
    return average * 3.9 / (4.095 * 0.774 * 15.6 * 0.8)

# Function to set current on load [mA], step 0.052[mA], range 0-211.5[mA]
def set_current(current):
    dac.write(int(current*DAC_coefficient))
