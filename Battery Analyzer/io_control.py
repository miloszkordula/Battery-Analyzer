from machine import Pin, I2C, SPI, sleep, ADC, freq # type: ignore
import mcp4725
# ADC configuration
samples = 16

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
    resistance = 15.6 #[Ohm]
    dac_output = int((4096*current*resistance*0.84)/3300)
    dac.write(dac_output)