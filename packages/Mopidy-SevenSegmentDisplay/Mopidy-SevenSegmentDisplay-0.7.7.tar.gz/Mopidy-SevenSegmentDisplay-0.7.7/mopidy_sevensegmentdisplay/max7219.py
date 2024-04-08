
class Constants(object):
    MAX7219_REG_NOOP = 0x0
    MAX7219_REG_DIGIT0 = 0x1
    MAX7219_REG_DIGIT1 = 0x2
    MAX7219_REG_DIGIT2 = 0x3
    MAX7219_REG_DIGIT3 = 0x4
    MAX7219_REG_DIGIT4 = 0x5
    MAX7219_REG_DIGIT5 = 0x6
    MAX7219_REG_DIGIT6 = 0x7
    MAX7219_REG_DIGIT7 = 0x8
    MAX7219_REG_DECODEMODE = 0x9
    MAX7219_REG_INTENSITY = 0xA
    MAX7219_REG_SCANLIMIT = 0xB
    MAX7219_REG_SHUTDOWN = 0xC
    MAX7219_REG_DISPLAYTEST = 0xF


class Symbols(object):
    NUMBER = [0x7e, 0x30, 0x6d, 0x79, 0x33, 0x5b, 0x5f, 0x70, 0x7f, 0x7b]
    BOTTOM = 0x08
    TOP = 0x40
    LEFT_TOP = 0x02
    LEFT_BOTTOM = 0x04
    RIGHT_TOP = 0x20
    RIGHT_BOTTOM = 0x10
    MIDDLE = 0x1
    NONE = 0
    DOT = 0x80
    A = int('01110111', 2)
    B = int('00011111', 2)
    C = int('01001110', 2)
    D = int('00111101', 2)
    E = int('01001111', 2)
    F = int('01000111', 2)
    # G
    H = int('00110111', 2)
    I = int('00110000', 2)
    J = int('00111100', 2)
    # K
    L = int('00001110', 2)
    M1 = int('00010101', 2)
    M2 = int('00010001', 2)
    N = int('00010101', 2)
    O = int('01111110', 2)
    P = int('01100111', 2)
    # Q
    R = int('00000101', 2)
    S = int('01011011', 2)
    T1 = int('01000000', 2)
    T2 = int('01000110', 2)
    U = int('00111110', 2)
    # V
    W1 = int('00011100', 2)
    W2 = int('00011000', 2)
    # X
    Y = int('00110011', 2)
    # Z


class SevenSegmentDisplay(object):
    NUM_DIGITS = 8

    def __init__(self, cascaded=1, spi_bus=0, spi_device=0, brightness=0):
        import spidev
        assert cascaded > 0, "Must have at least one device!"

        self._cascaded = cascaded
        self._buffer = [0] * self.NUM_DIGITS * self._cascaded
        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_device)
        self._spi.cshigh = False
        self._spi.max_speed_hz = 488000

        self.command(Constants.MAX7219_REG_SCANLIMIT, 7)    # show all 8 digits
        self.command(Constants.MAX7219_REG_DECODEMODE, 0)   # use matrix (not digits)
        self.command(Constants.MAX7219_REG_DISPLAYTEST, 0)  # no display test
        self.shutdown(False)                                # not shutdown mode
        self.set_brightness(brightness)                     # intensity: range: 0..15
        self.clear()

    def shutdown(self, value):
        self.command(Constants.MAX7219_REG_SHUTDOWN, 0 if value else 1)

    def stop(self):
        self._spi.close()

    def command(self, register, data):
        assert Constants.MAX7219_REG_DECODEMODE <= register <= Constants.MAX7219_REG_DISPLAYTEST

        self._write([register, data] * self._cascaded)

    def _write(self, data):
        self._spi.xfer2(list(data))

    def _values(self, position, buf):
        for deviceId in range(self._cascaded):
            yield position + Constants.MAX7219_REG_DIGIT0
            yield buf[(deviceId * self.NUM_DIGITS) + position]

    def clear(self, deviceId=None):
        assert not deviceId or 0 <= deviceId < self._cascaded, "Invalid deviceId: {0}".format(deviceId)

        if deviceId is None:
            start = 0
            end = self._cascaded
        else:
            start = deviceId
            end = deviceId + 1

        for deviceId in range(start, end):
            for position in range(self.NUM_DIGITS):
                self.set_byte(deviceId, position + Constants.MAX7219_REG_DIGIT0, 0)

        self.flush()

    def flush(self):
        buf = list(self._buffer)
        for posn in range(self.NUM_DIGITS):
            self._write(self._values(posn, buf))

    def set_brightness(self, intensity):
        assert 0 <= intensity < 16, "Invalid brightness: {0}".format(intensity)

        self.command(Constants.MAX7219_REG_INTENSITY, intensity)

    def set_byte(self, deviceId, position, value):
        assert 0 <= deviceId < self._cascaded, "Invalid deviceId: {0}".format(deviceId)
        assert Constants.MAX7219_REG_DIGIT0 <= position <= Constants.MAX7219_REG_DIGIT7, "Invalid digit/column: {0}".format(position)
        assert 0 <= value < 256, 'Value {0} outside range 0..255'.format(value)

        offset = (deviceId * self.NUM_DIGITS) + position - Constants.MAX7219_REG_DIGIT0
        self._buffer[offset] = value

    def set_buffer(self, buffer):
        assert len(buffer) == len(self._buffer), "Buffer is wrong size"

        length = len(buffer)
        for deviceId in range(0, self._cascaded):
            for position in range(self.NUM_DIGITS):
                pos = (deviceId * self.NUM_DIGITS) + position
                self.set_byte(deviceId, length - pos, buffer[pos])

    def scroll_left(self, value=0):
        assert 0 <= value < 256, 'Value {0} outside range 0..255'.format(value)

        del self._buffer[-1]
        self._buffer.insert(0, value)

    def scroll_right(self, value=0):
        assert 0 <= value < 256, 'Value {0} outside range 0..255'.format(value)

        del self._buffer[0]
        self._buffer.append(value)

    def scroll_down(self, buffer=None, index=0):
        if (buffer is not None):
            assert len(buffer) == len(self._buffer), "Buffer is wrong size"

        length = len(self._buffer)
        for i in range(length):
            byte = 0

            if (index < 3):
                byte |= self._switch_bit(self._buffer[i], 0, 3)
                byte |= self._switch_bit(self._buffer[i], 6, 0)
                byte |= self._switch_bit(self._buffer[i], 5, 4)
                byte |= self._switch_bit(self._buffer[i], 1, 2)

            if (buffer is not None):
                pos = length - i - 1
                if (index == 1):
                    byte |= self._switch_bit(buffer[pos], 3, 6)
                elif (index == 2):
                    byte |= self._switch_bit(buffer[pos], 0, 6)
                    byte |= self._switch_bit(buffer[pos], 3, 0)
                    byte |= self._switch_bit(buffer[pos], 4, 5)
                    byte |= self._switch_bit(buffer[pos], 2, 1)
                elif (index >= 3):
                    byte = buffer[pos]

            self._buffer[i] = byte

    def scroll_up(self, buffer=None, index=0):
        if (buffer is not None):
            assert len(buffer) == len(self._buffer), "Buffer is wrong size"

        length = len(self._buffer)
        for i in range(length):
            byte = 0

            if (index < 3):
                byte |= self._switch_bit(self._buffer[i], 3, 0)
                byte |= self._switch_bit(self._buffer[i], 0, 6)
                byte |= self._switch_bit(self._buffer[i], 4, 5)
                byte |= self._switch_bit(self._buffer[i], 2, 1)

            if (buffer is not None):
                pos = length - i - 1
                if (index == 1):
                    byte |= self._switch_bit(buffer[pos], 6, 3)
                elif (index == 2):
                    byte |= self._switch_bit(buffer[pos], 6, 0)
                    byte |= self._switch_bit(buffer[pos], 0, 3)
                    byte |= self._switch_bit(buffer[pos], 5, 4)
                    byte |= self._switch_bit(buffer[pos], 1, 2)
                elif (index >= 3):
                    byte = buffer[pos]

            self._buffer[i] = byte

    def _switch_bit(self, number, index_src, index_des):
        bit_value = ((number >> index_src) & 1) << index_des
        return bit_value
