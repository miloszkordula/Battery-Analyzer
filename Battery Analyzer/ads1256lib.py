from machine import Pin, SPI # type: ignore
import time

class ADS1256:

    # ADS1256 commands
    CMD_WAKEUP   = 0x00
    CMD_RDATA    = 0x01
    CMD_RDATAC   = 0x03
    CMD_SDATAC   = 0x0F
    CMD_RREG     = 0x10
    CMD_WREG     = 0x50
    CMD_SYNC     = 0xFC
    CMD_RESET    = 0xFE


    def __init__(self, spi, cs, drdy, sync, voltage_coef, current_coef):
        self.spi = spi
        self.cs = cs
        self.drdy = drdy 
        self.sync = sync

        self.voltage_coef = voltage_coef
        self.current_coef = current_coef

        try:
            self.configure_adc()
            print("ADS ADS1256 init OK")
        except Exception as e:
            print(f"ADS initialization error: {str(e)}")
        

    def send_command(self, cmd):
        self.spi.write(bytearray([cmd]))
        time.sleep_us(4)

    def write_register(self, reg, value):
        self.spi.write(bytearray([self.CMD_WREG | reg, 0x00, value]))  # Write 1 reg
        time.sleep_us(4)

    def read_registers(self, start_reg=0x00, count=11):
        self.spi.write(bytearray([self.CMD_RREG | start_reg, count - 1]))
        values = self.spi.read(count)
        return values

    def wait_for_drdy(self, timeout_us=1_000_000):
        start = time.ticks_us()
        while self.drdy.value() == 1:
            if time.ticks_diff(time.ticks_us(), start) > timeout_us:
                print("ADS Timeout waiting for DRDY")
                return False
            time.sleep_us(2)
        if time.ticks_diff(time.ticks_us(), start) > 100:
            print(f"ADS Waited {time.ticks_diff(time.ticks_us(), start)} us for drdy")
        return True

    def read_data(self, coef):
        if not self.wait_for_drdy():
            return None
        self.spi.write(bytearray([self.CMD_RDATA]))
        time.sleep_us(10)
        raw = self.spi.read(3)
        value = (raw[0] << 16) | (raw[1] << 8) | raw[2]
        if value & 0x800000:
            value -= 0x1000000

        value = value * coef
        return value
    
    

    def set_channel(self, pos, neg=0x08):  # Single-ended (AINx - AINCOM)
        mux = (pos << 4) | neg
        self.write_register(0x01, mux)  # MUX
        self.send_command(self.CMD_SYNC)
        self.send_command(self.CMD_WAKEUP)
        #time.sleep_us(210)

    def configure_adc(self):
        print("Resetting ADS1256...")
        self.send_command(self.CMD_RESET)
        time.sleep_ms(10)
        self.send_command(self.CMD_WAKEUP)

        # Write key config registers
        self.write_register(0x00, 0x02)  # STATUS: Auto-Calibration ON
        self.write_register(0x02, 0x00)  # ADCON: Gain=1, Clock off
        self.write_register(0xF0, 0x82)  # DRATE: 30,000 SPS

        # Read and dump all 11 registers
        print("Reading ADS1256 registers after reset:")
        regs = self.read_registers()
        for i, val in enumerate(regs):
            print(f"Reg 0x{i:02X} = 0x{val:02X}")
        self.set_channel(0)
        time.sleep_us(210)

    

    def get_reading_ADS1256(self):
        current = self.read_data(self.current_coef)

        self.set_channel(1)
        time.sleep_us(210)
        voltage = self.read_data(self.voltage_coef)

        self.set_channel(0)

        return voltage, current
