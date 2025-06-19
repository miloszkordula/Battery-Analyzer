from discharge_control import discharge, eis

class Settings:
    start_voltage = 800_000_0 #0.1uV
    end_voltage = 500_000_0 #0.1uV

    repetitions = 60
    filter_voltage = 50_000_0 #0.1uV


    #discharge(Current [mA], Time[us], Log_downsample)
    #eis(Max Current [mA], Min Freq [Hz], Max Freq [Hz], No of points)
    def Program(self):
        
        discharge(self, 0, 60_000_000, 100)

        eis(self, 200, 0.05, 50, 40)
        
        discharge(self, 420, 900_000_000, 20)
