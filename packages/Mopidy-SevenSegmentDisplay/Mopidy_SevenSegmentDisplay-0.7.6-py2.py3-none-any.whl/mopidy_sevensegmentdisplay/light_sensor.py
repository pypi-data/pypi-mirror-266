import time
from datetime import datetime
from .max7219 import Symbols
from .threader import Threader

class LightSensor(Threader):
    S = Symbols.S
    L = Symbols.L
    E = Symbols.E
    P = Symbols.P

    ANIMATION_SLEEP = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, S],
            [0, 0, 0, 0, 0, 0, S, 0],
            [0, 0, 0, 0, 0, S, 0, 0],
            [0, 0, 0, 0, S, 0, 0, 0],
            [0, 0, 0, S, 0, 0, 0, 0],
            [0, 0, S, 0, 0, 0, 0, L],
            [0, 0, S, 0, 0, 0, L, 0],
            [0, 0, S, 0, 0, L, 0, 0],
            [0, 0, S, 0, L, 0, 0, 0],
            [0, 0, S, L, 0, 0, 0, E],
            [0, 0, S, L, 0, 0, E, 0],
            [0, 0, S, L, 0, E, 0, 0],
            [0, 0, S, L, E, 0, 0, E],
            [0, 0, S, L, E, 0, E, 0],
            [0, 0, S, L, E, E, 0, 0],
            [0, 0, S, L, E, E, 0, P],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, L, E, E, P, 0]
        ]
    }

    _max_value = 26000
    _channel = None
    _value = 0.5

    def __init__(self, enabled, timeout, sudden_change_callback, sudden_change_timeout_callback):
        super(LightSensor, self).__init__()
        
        self._timeout = timeout
        self._sudden_change_callback = sudden_change_callback
        self._sudden_change_timeout_callback = sudden_change_timeout_callback

        if (not enabled):
            return

        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        # Initialize the I2C interface
        self._i2c = busio.I2C(board.SCL, board.SDA)

        # Create an ADS1115 object
        self._ads = ADS.ADS1115(self._i2c)

        # Define the analog input channel
        self._channel = AnalogIn(self._ads, ADS.P0)

        super(LightSensor, self).start()

    def run(self):
        previous_value = self.read_value()
        timeout = -1
        min_value = 200 / self._max_value
        max_value = 500 / self._max_value

        while (True):
            if (self.stopped()):
                break

            self._value = self.read_value()

            if (self._value < min_value and previous_value > max_value):
                self._sudden_change_callback(datetime.now(), True)
                timeout = 0
            elif (self._value > max_value and previous_value < min_value):
                self._sudden_change_callback(datetime.now(), False)
                timeout = 0

            if (timeout > self._timeout * 60 * 10):
                self._sudden_change_timeout_callback()
                timeout = -1

            previous_value = self._value

            if (timeout >= 0):
                timeout += 1

            time.sleep(0.1)

        self._i2c.deinit()

    def read_value(self):
        if (self._channel is None):
            return 0.5

        value = self._channel.value

        if (value > self._max_value):
            return 1

        return value / self._max_value
    
    def get_value(self):
        return self._value
    
    def get_draw_sleep_animation(self):
        return self.ANIMATION_SLEEP
