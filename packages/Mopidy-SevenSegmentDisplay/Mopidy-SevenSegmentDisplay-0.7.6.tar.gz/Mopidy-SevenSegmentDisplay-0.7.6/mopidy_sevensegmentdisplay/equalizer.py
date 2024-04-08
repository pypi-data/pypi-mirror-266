import os
import struct
import subprocess
import logging
import configparser
import pathlib
from .max7219 import Symbols


class Equalizer:

    def __init__(self, display, music, equalizer_enabled):
        self._display = display
        self._music = music
        self._equalizer_enabled = equalizer_enabled
        self._process = None

        self._sample = [
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE
        ]

        self._config_file_name = str(pathlib.Path(__file__).parent.resolve()) + '/cava.config'
            
        logging.info('cava config: ' + self._config_file_name)

        config = configparser.RawConfigParser()
        config.read(self._config_file_name)

        general_bars = int(config.get('general', 'bars'))
        self._output_raw_target = config.get('output', 'raw_target')
        output_bit_format = config.get('output', 'bit_format')

        bytetype = "H" if output_bit_format == "16bit" else "B"
        bytesize = 2 if output_bit_format == "16bit" else 1
        self._bytenorm = 65535 if output_bit_format == "16bit" else 255
        self._chunk = bytesize * general_bars
        self._fmt = bytetype * general_bars

    def is_visible(self):
        return self._equalizer_enabled and self._music.is_playing()

    def run(self):
        if (self._process is None):
            self._process = subprocess.Popen(["cava", "-p", self._config_file_name], stdout=subprocess.PIPE)

            if (self._output_raw_target != "/dev/stdout"):
                if (not os.path.exists(self._output_raw_target)):
                    os.mkfifo(self._output_raw_target)
                self._source = open(self._output_raw_target, "rb")
            else:
                self._source = self._process.stdout

        self._display.draw(self._get_draw_buffer())

    def stop(self):
        if (self._process is not None):
            self._source.close()
            self._source = None
            self._process.terminate()
            self._process = None

    def _get_draw_buffer(self):
        if (self._source is not None):
            data = self._source.read(self._chunk)
            if (len(data) < self._chunk):
                return self._sample
            self._sample = [self._get_symbol(i / self._bytenorm) for i in struct.unpack(self._fmt, data)]

        return self._sample

    def _get_symbol(self, ratio):
        if (ratio > 0.8):
            return Symbols.TOP | Symbols.MIDDLE | Symbols.BOTTOM
        elif (ratio > 0.4):
            return Symbols.MIDDLE | Symbols.BOTTOM
        elif (ratio > 0.1):
            return Symbols.BOTTOM
        return Symbols.NONE
