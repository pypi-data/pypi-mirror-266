import time
import logging
from subprocess import call


class IrSender:
    POWER = "power"
    VOL_DOWN = "vol-"
    VOL_UP = "vol+"
    BASS_DOWN = "bass-"
    BASS_UP = "bass+"

    def __init__(self, ir_remote, on_power):
        self._ir_remote = ir_remote
        self._on_power = on_power
        self._is_power_on = False

    def stop(self):
        self.power(False)

    def power(self, value=None):
        if (value is None or value != self._is_power_on):
            self._on_power(value)
            self._send(self._ir_remote, self.POWER)
            self._is_power_on = value

    def volume(self, value, sleep=0.2):
        command = self.VOL_UP if value > 0 else self.VOL_DOWN
        for i in range(abs(value)):
            self._send(self._ir_remote, command)
            time.sleep(sleep)

    def bass(self, value, sleep=0.2):
        command = self.BASS_UP if value > 0 else self.BASS_DOWN
        for i in range(abs(value)):
            self._send(self._ir_remote, command)
            time.sleep(sleep)

    def _send(self, remote, command):
        try:
            call(["irsend", "SEND_ONCE", remote, command])
        except Exception as inst:
            logging.error(inst)
