from discharge_control import discharge, eis

class Settings:
    repetitions = 60


    #discharge(Current [mA], Time[us], Log_downsample)
    #eis(Max Current [mA], Min Freq [Hz], Max Freq [Hz], No of points)
    #eis_continous(Max Current [mA], Min Freq [Hz], Max Freq [Hz], No of points)
    def Program(self):
        
        discharge(0, 60_000_000, 100)

        eis(100, 0.1, 20, 40)
        
        discharge(420, 900_000_000, 20)
