from datetime import datetime
from .max7219 import Symbols


class Time:
    VISIBLE_FOR_SECONDS = 5

    def __init__(self):
        self._blink = True

    def run(self):
        pass

    def is_visible(self, seconds):
        return seconds < self.VISIBLE_FOR_SECONDS

    def get_draw_buffer(self):
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second

        self._blink = not self._blink

        separator = Symbols.NONE
        if (self._blink):
            separator = Symbols.MIDDLE

        time = [
            Symbols.NUMBER[int(hour / 10)],
            Symbols.NUMBER[hour % 10],
            separator,
            Symbols.NUMBER[int(minute / 10)],
            Symbols.NUMBER[minute % 10],
            separator,
            Symbols.NUMBER[int(second / 10)],
            Symbols.NUMBER[second % 10]
        ]

        return time


class Date:
    VISIBLE_FOR_SECONDS = 2

    def __init__(self, modules):
        self._modules = modules

    def run(self):
        pass

    def is_visible(self, seconds):
        return seconds < self.VISIBLE_FOR_SECONDS and not self._is_any_module_enabled()

    def get_draw_buffer(self):
        now = datetime.now()
        day = now.day
        month = now.month
        year = now.year

        date = [
            Symbols.NUMBER[int(year / 1000)],
            Symbols.NUMBER[int(year / 100) % 10],
            Symbols.NUMBER[int(year / 10) % 10],
            Symbols.NUMBER[year % 10] + Symbols.DOT,
            Symbols.NUMBER[int(month / 10)],
            Symbols.NUMBER[month % 10] + Symbols.DOT,
            Symbols.NUMBER[int(day / 10)],
            Symbols.NUMBER[day % 10]
        ]

        return date

    def _is_any_module_enabled(self):
        for module in self._modules:
            if (module.is_set()):
                return True
        return False
