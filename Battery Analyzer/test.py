import io_control
import logging




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



