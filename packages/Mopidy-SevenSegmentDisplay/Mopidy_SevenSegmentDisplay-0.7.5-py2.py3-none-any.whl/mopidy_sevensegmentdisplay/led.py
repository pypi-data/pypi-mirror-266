import colorsys
import random
import logging
import RPi.GPIO as GPIO
from .lib_nrf24 import NRF24


class Led:
    
    def __init__(self, led_enabled):
        self._radio = None
        self._pipes = []
        self._size = 8

        if (not led_enabled):
            return

        GPIO.setmode(GPIO.BCM)
        
        readingPipe = [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]

        import spidev
        spi = spidev.SpiDev()
        spi.open(0, 1)
        spi.cshigh = False
        spi.max_speed_hz = 500000
        spi.mode = 0

        self._radio = NRF24(GPIO, spi)
        self._radio.begin(1, 25)

        self._radio.setPayloadSize(self._size)
        self._radio.setChannel(0x76)
        self._radio.setDataRate(NRF24.BR_1MBPS)
        self._radio.setPALevel(NRF24.PA_MAX)
        self._radio.setAutoAck(True)
        self._radio.openReadingPipe(1, readingPipe)
        self._radio.printDetails()

        self._radio.startListening()

    def run(self):
        if self._radio.available():
            r = []

            self._radio.read(r, self._size)

            logging.info(r)

            if (r[0] != 1):
                return

            for pipe in self._pipes:
                if (pipe[0] == r[1] and
                    pipe[1] == r[2] and
                    pipe[2] == r[3] and
                    pipe[3] == r[4] and
                    pipe[4] == r[5]):
                    return

            self._pipes.append([r[1], r[2], r[3], r[4], r[5]])


    def setColor(self, red, green, blue):
        try:
            if self._radio is None:
                return

            self._radio.stopListening()

            for pipe in self._pipes:
                self._radio.openWritingPipe(pipe);

                self._radio.write([0, red, green, blue])

                if self._radio.isAckPayloadAvailable():
                    buffer = []
                    self._radio.read(buffer, self._radio.getDynamicPayloadSize())
                    logging.info("NRF24 ACK Received:"),
                    logging.info(buffer)
                else:
                    logging.info("Received: Ack only, no payload")

            self._radio.startListening()
        except Exception as inst:
            logging.error(inst)
        
    def setColorHsv(self, hue, sat = 1, val = 1):
        c = colorsys.hsv_to_rgb(hue / 360.0, sat, val)
            
        self.setColor(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))

    def setRandomColor(self):
        self.setColorHsv(random.random() * 360)

    def setNoneColor(self):
        self.setColor(0, 0, 0)
