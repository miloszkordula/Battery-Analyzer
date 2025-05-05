import time

class ExtendedTicksUS:
    def __init__(self):
        self._last_ticks = time.ticks_us()
        self._high_part = 0
        self._time_offset = 0
        self._max_ticks = 2**30  # 32-bit counter max value

    def _update(self):
        current_ticks = time.ticks_us()
        if current_ticks < self._last_ticks:
            # Overflow occurred
            self._high_part += self._max_ticks
        self._last_ticks = current_ticks

    def abs_ticks_us(self):
        self._update()
        return self._high_part + self._last_ticks 

    def ticks_us(self):
        self._update()
        return self._high_part + self._last_ticks - self._time_offset
    
    def set_offset(self, offset):
        self._time_offset += offset


global_time_tracker = ExtendedTicksUS()