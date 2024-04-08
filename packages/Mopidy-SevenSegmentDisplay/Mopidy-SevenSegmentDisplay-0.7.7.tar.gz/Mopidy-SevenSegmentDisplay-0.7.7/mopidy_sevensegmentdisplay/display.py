import threading
import logging
from .max7219 import SevenSegmentDisplay, Symbols
from .animation import Animation, BlinkAnimation, ScrollDownAnimation, ScrollUpAnimation, ScrollLeftAnimation, ScrollRightAnimation


class Display(object):

    def __init__(self, display_enabled):
        self._brightness = None
        self._is_shutdown = not display_enabled
        self._animation_thread = None
        self._display = SevenSegmentDisplay() if display_enabled else None
        self._lock = threading.Lock()

    def set_brightness(self, brightness):
        if (self._display is None):
            return

        if (self._brightness != brightness):
            self._brightness = brightness
            self._display.set_brightness(brightness)

    def shutdown(self, is_shutdown=True):
        if (self._display is None):
            return

        if (self._is_shutdown != is_shutdown):
            if (is_shutdown):
                self._kill_animation()
            self._is_shutdown = is_shutdown
            self._display.shutdown(is_shutdown)

    def stop(self):
        if (self._display is None):
            return
        
        self.shutdown()
        self._display.stop()
        self._display = None


    def draw(self, buffer):
        if (self._display is None):
            return
        
        self._kill_animation()
        self._display.set_buffer(buffer)
        self._display.flush()

    def draw_animation(self, buffer, repeat=1, sleep=0.05):
        if (self._display is None):
            return

        self._draw_animation(Animation(self._display, buffer, repeat, sleep))

    def draw_blink_animation(self, buffer, repeat=6, sleep=0.1):
        if (self._display is None):
            return

        self._draw_animation(BlinkAnimation(self._display, buffer, repeat, sleep))

    def draw_scroll_left_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        new_buffer = list(buffer)
        new_buffer.insert(0, Symbols.NONE)
        self._draw_animation(ScrollLeftAnimation(self._display, new_buffer, sleep))

    def draw_scroll_right_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        new_buffer = list(buffer)
        new_buffer.append(Symbols.NONE)
        self._draw_animation(ScrollRightAnimation(self._display, new_buffer, sleep))

    def draw_scroll_up_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        self._draw_animation(ScrollUpAnimation(self._display, buffer, sleep))

    def draw_scroll_down_animation(self, buffer, sleep=0.05):
        if (self._display is None):
            return

        self._draw_animation(ScrollDownAnimation(self._display, buffer, sleep))

    def _draw_animation(self, animation):
        self._lock.acquire()
        try:
            if (self._animation_thread is not None):
                self._animation_thread.stop()
                self._animation_thread = None
            if (animation is not None):
                self._animation_thread = animation
                self._animation_thread.start()
        except Exception as inst:
            logging.error(inst)
        finally:
            self._lock.release()

    def _kill_animation(self):
        self._draw_animation(None)


class DisplayWithPowerSaving(Display):

    def __init__(self, display_enabled, light_sensor, display_min_brightness, display_max_brightness):
        super(DisplayWithPowerSaving, self).__init__(display_enabled)
        self._light_sensor = light_sensor
        self._display_min_brightness = display_min_brightness
        self._display_max_brightness = display_max_brightness

    def update_brightness(self):
        value = self._light_sensor.get_value()

        brightness = int(round(self._display_min_brightness + (self._display_max_brightness - self._display_min_brightness) * value))
        
        super(DisplayWithPowerSaving, self).set_brightness(brightness)
