import io_control
import logging
from ina219 import INA219

# INA219 initialization
SHUNT_OHMS = 0.1
ina = INA219(SHUNT_OHMS, io_control.i2c)
ina.configure(voltage_range=INA219.RANGE_16V, gain=INA219.GAIN_1_40MV)

def initialize_dac():
    try:
        eeprom_write_busy,power_down,value,eeprom_power_down,eeprom_value = io_control.dac.read()
        print ("DAC DAC init OK")
        #return "DAC DAC init OK"
    except Exception as e:
        print(f"DAC initialization error: {str(e)}")
        #return f"DAC initialization error: {str(e)}"
    
def scan_i2c():
    print('I2C Scan i2c bus...')
    devices = io_control.i2c.scan()

    if len(devices) == 0:
        print("I2C No i2c device !")
    else:
        print('I2C i2c devices found:',len(devices))

    for device in devices:  
        print("Decimal address: ",device," | Hexa address: ",hex(device))


def oversample(adc, samples):
    start_time = logging.time.ticks_us()
    total = 0
    for _ in range(samples):
        total += adc.read()
    average = total / samples
    end_time = logging.time.ticks_us()
    elapsed_time = logging.time.ticks_diff(end_time, start_time)
    return average * 3.9 / (4.095 * 0.774), elapsed_time




# Function to test INA219
def test_ina219():
    try:
        #voltage = ina.voltage()
        voltage, elapsed_time = oversample(io_control.adc, io_control.samples)

        current = ina.shunt_voltage()*10
        return f"INA219 OK: {voltage:.1f}mV {current:.1f}mA", elapsed_time
    except Exception as e:
        return f"INA219 Error: {str(e)}", 0