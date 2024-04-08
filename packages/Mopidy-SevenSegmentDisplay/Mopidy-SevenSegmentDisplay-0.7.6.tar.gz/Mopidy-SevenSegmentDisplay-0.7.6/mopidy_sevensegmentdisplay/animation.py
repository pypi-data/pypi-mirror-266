import time
from .threader import Threader


class Animation(Threader):

    def __init__(self, display, buffer, repeat, sleep):
        super(Animation, self).__init__()
        self._display = display
        self._buffer = buffer
        self._repeat = repeat
        self._sleep = sleep

    def run(self):
        for j in range(self._repeat):
            for i in range(len(self._buffer)):
                if (self.stopped()):
                    break
                self._display.set_buffer(self._buffer[i])
                self._display.flush()
                time.sleep(self._sleep)
            if (self.stopped()):
                break


class BlinkAnimation(Threader):

    def __init__(self, display, buffer, repeat, sleep):
        super(BlinkAnimation, self).__init__()
        self._display = display
        self._buffer = buffer
        self._repeat = repeat
        self._sleep = sleep

    def run(self):
        for j in range(self._repeat):
            if (self.stopped()):
                break
            if (j % 2 == 1):
                self._display.set_buffer(self._buffer)
            else:
                self._display.clear()
            self._display.flush()
            time.sleep(self._sleep)


class ScrollLeftAnimation(Threader):

    def __init__(self, display, buffer, sleep):
        super(ScrollLeftAnimation, self).__init__()
        self._display = display
        self._buffer = buffer
        self._sleep = sleep

    def run(self):
        for i in range(len(self._buffer)):
            if (self.stopped()):
                break
            self._display.scroll_left(self._buffer[i])
            self._display.flush()
            time.sleep(self._sleep)


class ScrollRightAnimation(Threader):

    def __init__(self, display, buffer, sleep):
        super(ScrollRightAnimation, self).__init__()
        self._display = display
        self._buffer = buffer
        self._sleep = sleep

    def run(self):
        length = len(self._buffer)
        for i in range(length):
            if (self.stopped()):
                break
            self._display.scroll_right(self._buffer[length - i - 1])
            self._display.flush()
            time.sleep(self._sleep)


class ScrollUpAnimation(Threader):
    FROM = -1
    TO = 4

    def __init__(self, display, buffer, sleep):
        super(ScrollUpAnimation, self).__init__()
        self._display = display
        self._buffer = buffer
        self._sleep = sleep

    def run(self):
        for i in range(self.FROM, self.TO):
            if (self.stopped()):
                break
            self._display.scroll_up(self._buffer, i)
            self._display.flush()
            time.sleep(self._sleep)


class ScrollDownAnimation(Threader):
    FROM = -1
    TO = 4

    def __init__(self, display, buffer, sleep):
        super(ScrollDownAnimation, self).__init__()
        self._display = display
        self._buffer = buffer
        self._sleep = sleep

    def run(self):
        for i in range(self.FROM, self.TO):
            if (self.stopped()):
                break
            self._display.scroll_down(self._buffer, i)
            self._display.flush()
            time.sleep(self._sleep)
