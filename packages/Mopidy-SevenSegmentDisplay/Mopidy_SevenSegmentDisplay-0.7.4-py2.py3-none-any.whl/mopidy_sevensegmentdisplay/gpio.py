import RPi.GPIO as GPIO
import threading
import time
import logging


class Gpio:
    POWER_BUTTON_PIN = 12  # StandBy-On
    MENU_BUTTON_PIN = 13   # Open/Close
    LEFT_BUTTON_PIN = 5    # Play/Pause
    RIGHT_BUTTON_PIN = 6   # Stop
    RELAY_PIN = 4

    def __init__(self, buttons_enabled, on_power, on_menu, on_left, on_right, relay_enabled):
        self._lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)

        if (buttons_enabled):
            GPIO.setup(self.POWER_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.MENU_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.LEFT_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.RIGHT_BUTTON_PIN, GPIO.IN)

            GPIO.add_event_detect(self.POWER_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_power() if not self._lock.locked() else None)
            GPIO.add_event_detect(self.MENU_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_menu() if not self._lock.locked() else None)
            GPIO.add_event_detect(self.LEFT_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_left() if not self._lock.locked() else None)
            GPIO.add_event_detect(self.RIGHT_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_right() if not self._lock.locked() else None)

        if (relay_enabled):
            self._is_relay_on = False
            GPIO.setup(self.RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)

        self._relay_enabled = relay_enabled

    def switch_relay(self, value):
        if (self._relay_enabled and self._lock.acquire()):
            try:
                if (value != self._is_relay_on):
                    GPIO.output(self.RELAY_PIN, GPIO.LOW if value else GPIO.HIGH)
                    self._is_relay_on = value
                    time.sleep(1)
                    return True
            except Exception as inst:
                logging.error(inst)
            finally:
                threading.Timer(1, self._lock.release).start()
        return False

    def cleanup(self):
        GPIO.cleanup()
