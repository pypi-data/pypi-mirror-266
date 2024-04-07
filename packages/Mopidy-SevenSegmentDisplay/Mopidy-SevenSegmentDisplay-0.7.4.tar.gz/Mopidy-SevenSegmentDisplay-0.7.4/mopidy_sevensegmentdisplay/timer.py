from datetime import datetime, timedelta
from .max7219 import Symbols


class Timer(object):
    VISIBLE_FOR_SECONDS = 2

    def __init__(self, callback, step, remove_min=True):
        self._callback = callback
        self._step = step
        self._half_step = int(step / 2)
        self._remove_min = remove_min
        self._now = self._datetime_now()
        self._timer = None

    def run(self):
        self._now = self._datetime_now()
        if (self.is_set()):
            if (self._is_time()):
                self._callback()
                self.reset()

    def is_set(self):
        return self._timer is not None

    def _datetime_now(self):
        return datetime.now().replace(second=0, microsecond=0)

    def _is_time(self):
        return self._now >= self._timer

    def reset(self):
        self._timer = None

    def get(self):
        return self._timer

    def set(self, hour=None, minute=None):
        if (hour is not None or minute is not None):
            new_timer = self._now
            if (hour is not None):
                new_timer = new_timer.replace(hour=int(hour))
            if (minute is not None):
                new_timer = new_timer.replace(minute=int(minute))
            if (new_timer <= self._now):
                new_timer += timedelta(days=1)
            self._timer = new_timer

    def increase(self):
        if (not self.is_set()):
            time_left = (self._step - self._now.minute % self._step) if self._remove_min else 0
            min = time_left + (self._step if time_left < self._half_step else 0)
            self._timer = self._now + timedelta(minutes=min)
        else:
            new_time = self._timer + timedelta(minutes=self._step)
            diff = new_time - self._now
            if (diff.days < 1):
                self._timer = new_time

    def decrease(self):
        if (self.is_set()):
            timer_minus_step = self._timer - timedelta(minutes=self._step)
            now_plus_half_step = self._now + timedelta(minutes=self._half_step)
            if (now_plus_half_step < timer_minus_step):
                self._timer = timer_minus_step
            else:
                self._timer = None

    def is_visible(self, seconds):
        return seconds < self.VISIBLE_FOR_SECONDS and self.is_set()


class TimerOff(Timer):
    TIMER_STEP = 30

    def __init__(self, callback):
        super(TimerOff, self).__init__(callback, self.TIMER_STEP)

    def get_draw_buffer(self):
        if (self.is_set()):
            timer = self.get()
            hour = timer.hour
            minute = timer.minute
            return [
                Symbols.O,
                Symbols.F,
                Symbols.F,
                Symbols.NONE,
                Symbols.NUMBER[int(hour / 10)],
                Symbols.NUMBER[hour % 10] + Symbols.DOT,
                Symbols.NUMBER[int(minute / 10)],
                Symbols.NUMBER[minute % 10]
            ]
        else:
            return [
                Symbols.O,
                Symbols.F,
                Symbols.F,
                Symbols.NONE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE
            ]


class TimerOn(Timer):
    TIMER_STEP = 30

    def __init__(self, callback):
        super(TimerOn, self).__init__(callback, self.TIMER_STEP)

    def get_draw_buffer(self):
        if (self.is_set()):
            timer = self.get()
            hour = timer.hour
            minute = timer.minute
            return [
                Symbols.O,
                Symbols.N,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NUMBER[int(hour / 10)],
                Symbols.NUMBER[hour % 10] + Symbols.DOT,
                Symbols.NUMBER[int(minute / 10)],
                Symbols.NUMBER[minute % 10]
            ]
        else:
            return [
                Symbols.O,
                Symbols.N,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE
            ]


class TimerAlert:
    TIMER_STEP = 10

    def __init__(self, callback):
        self._callback = callback
        self._timer_index = 0
        self._timers = []

    def get_draw_buffer(self):
        if (len(self._timers) > self._timer_index and self._timers[self._timer_index].is_set()):
            timer = self._timers[self._timer_index].get()
            hour = timer.hour
            minute = timer.minute
            return [
                Symbols.T1,
                Symbols.T2,
                Symbols.NUMBER[self._timer_index],
                Symbols.NONE,
                Symbols.NUMBER[int(hour / 10)],
                Symbols.NUMBER[hour % 10] + Symbols.DOT,
                Symbols.NUMBER[int(minute / 10)],
                Symbols.NUMBER[minute % 10]
            ]
        else:
            return [
                Symbols.T1,
                Symbols.T2,
                Symbols.NUMBER[self._timer_index],
                Symbols.NONE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE,
                Symbols.MIDDLE
            ]

    def get_draw_menu_buffer(self):
        if (self._have_timers()):
            self._timer_index = len(self._timers) - 1
        else:
            self._timer_index = 0
        return self.get_draw_buffer()

    def run(self):
        for i in range(len(self._timers) - 1, -1, -1):
            if (not self._timers[i].is_set()):
                del self._timers[i]
            else:
                self._timers[i].run()

    def add_timer(self, hour=None, minute=None):
        if (len(self._timers) < 10):
            new_timer = Timer(self._callback, self.TIMER_STEP, False)
            if (hour is not None or minute is not None):
                new_timer.set(hour, minute)
            else:
                if (self._have_timers()):
                    timer = self._timers[len(self._timers) - 1].get()
                    new_timer.set(timer.hour, timer.minute)
                for i in range(6):
                    new_timer.increase()
            self._timers.append(new_timer)

    def _have_timers(self):
        return len(self._timers) > 0

    def is_set(self):
        for timer in self._timers:
            if (timer.is_set()):
                return True
        return False

    def reset(self):
        self._timer_index = 0
        self._timers = []

    def get(self):
        return self._timers

    def increase(self):
        if (not self._have_timers()):
            self.add_timer()
        else:
            self._timers[len(self._timers) - 1].increase()

    def decrease(self):
        if (self._have_timers()):
            self._timers[len(self._timers) - 1].decrease()

    def is_visible(self, seconds):
        self._timer_index = seconds // Timer.VISIBLE_FOR_SECONDS
        return seconds < Timer.VISIBLE_FOR_SECONDS * len(self._timers)
