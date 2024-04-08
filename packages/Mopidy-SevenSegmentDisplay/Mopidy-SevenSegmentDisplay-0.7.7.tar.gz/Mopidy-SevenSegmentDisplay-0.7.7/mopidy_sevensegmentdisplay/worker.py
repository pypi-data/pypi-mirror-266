import logging
from time import sleep
from .equalizer import Equalizer
from .threader import Threader
from .light_sensor import LightSensor
from .music import Music
from .display import DisplayWithPowerSaving
from .ir import IrSender
from .gpio import Gpio
from .timer import TimerOn, TimerOff, TimerAlert
from .clock import Time, Date
from .menu import Menu
from .max7219 import Symbols
from .alert import Alert
from .led import Led


class Worker(Threader):
    core = None
    music = None
    display = None
    gpio = None
    light_sensor = None
    ir_sender = None
    timer_on = None
    timer_off = None
    alert = None
    timer_alert = None
    time = None
    date = None
    menu = None
    equalizer = None

    response_code = None

    def start(self, config, core):
        self.config = config
        self.core = core
        super(Worker, self).start()

    def run(self):
        try:
            self._init_menu()
            self.music = Music(self.core, self.config['default_tracks'], self.config['default_preset'])
            self.light_sensor = LightSensor(
                self.config['light_sensor_enabled'],
                self.config['light_sensor_timeout'],
                self._on_light_sensor_sudden_change,
                self._on_light_sensor_sudden_change_timeout)
            self.display = DisplayWithPowerSaving(
                self.config['display_enabled'],
                self.light_sensor,
                self.config['display_min_brightness'],
                self.config['display_max_brightness'])
            self.gpio = Gpio(
                self.config['buttons_enabled'],
                self.play_stop_music,
                self._on_menu_click,
                self._on_menu_click_left,
                self._on_menu_click_right,
                self.config['relay_enabled'])
            self.led = Led(self.config['led_enabled'])
            self.ir_sender = IrSender(self.config['ir_remote'], self.gpio.switch_relay)
            self.timer_on = TimerOn(self.play_music)
            self.timer_off = TimerOff(self.stop_music)
            self.alert = Alert(self.music,
                               self.ir_sender,
                               self.config['alert_files'])
            self.timer_alert = TimerAlert(self.run_alert)
            self.time = Time()
            self.date = Date([self.timer_on, self.timer_off, self.timer_alert])
            self.menu = Menu(
                self.display,
                self.MENU,
                [self.time, self.date, self.timer_on, self.timer_off, self.timer_alert])
            self.equalizer = Equalizer(self.display, self.music, self.config['equalizer_enabled'])

            while True:
                if (self.stopped()):
                    break

                if (self.equalizer.is_visible() and not self.menu.is_sub_menu_visible()):
                    self.equalizer.run()
                else:
                    self.equalizer.stop()
                    self.menu.run()
                    self.led.run()
                    sleep(1)

        except Exception as inst:
            logging.error(inst)
        finally:
            self.equalizer.stop()
            self.ir_sender.stop()
            self.led.set_none_color()
            self.gpio.cleanup()
            self.display.stop()
            self.light_sensor.stop()

    def _init_menu(self):
        self.MENU = {
            "get_sub_menu": lambda: [
                {
                    "get_sub_menu": lambda: [
                        self.MENU_TIMER,
                        self.MENU_PLAY_1,
                        self.MENU_RUN_SH,
                        self.MENU_VOLUME,
                        self.MENU_STYLE,
                        self.MENU_DEMO,
                        self.MENU_SYSTEM
                    ]
                }
            ]
        }
        self.MENU_TIMER = {
            "get_buffer": lambda: [0, Symbols.T1, Symbols.T2, Symbols.I, Symbols.M1, Symbols.M2, Symbols.E, Symbols.R],
            "get_sub_menu": lambda: [
                self.MENU_ALERT,
                self.MENU_TIMER_OFF,
                self.MENU_TIMER_ON
            ]
        }
        self.MENU_ALERT = {
            "get_buffer": lambda: [0, Symbols.A, Symbols.L, Symbols.E, Symbols.R, Symbols.T1, Symbols.T2, 0],
            "get_sub_menu": lambda: [
                self.MENU_ALERT_ADD,
                self.MENU_ALERT_CLEAR,
                self.MENU_ALERT_RUN
            ]
        }
        self.MENU_ALERT_ADD = {
            "get_buffer": lambda: [0, 0, 0, Symbols.A, Symbols.D, Symbols.D, 0, 0],
            "get_sub_menu": lambda: [
                {
                    "get_buffer": self.timer_alert.get_draw_menu_buffer,
                    "click": lambda: (self.timer_alert.add_timer(),
                                      self.display.draw(self.timer_alert.get_draw_menu_buffer())),
                    "click_left": self.timer_alert.decrease,
                    "click_right": self.timer_alert.increase
                }
            ]
        }
        self.MENU_ALERT_CLEAR = {
            "get_buffer": lambda: [0, 0, Symbols.C, Symbols.L, Symbols.E, Symbols.A, Symbols.R, 0],
            "click": lambda: self.timer_alert.reset(),
            "click_animation": True
        }
        self.MENU_ALERT_RUN = {
            "get_buffer": lambda: [0, 0, 0, Symbols.R, Symbols.U, Symbols.N, 0, 0],
            "click": lambda: self.run_alert(),
            "click_animation": True
        }
        self.MENU_TIMER_OFF = {
            "group": "timer_off",
            "get_buffer": lambda: [0, 0, 0, Symbols.O, Symbols.F, Symbols.F, 0, 0],
            "get_sub_menu": lambda: [
                {
                    "get_buffer": self.timer_off.get_draw_buffer,
                    "click_left": self.timer_off.decrease,
                    "click_right": self.timer_off.increase
                }
            ]
        }
        self.MENU_TIMER_ON = {
            "group": "timer_on",
            "get_buffer": lambda: [0, 0, 0, Symbols.O, Symbols.N, 0, 0, 0],
            "get_sub_menu": lambda: [
                {
                    "get_buffer": self.timer_on.get_draw_buffer,
                    "click_left": self.timer_on.decrease,
                    "click_right": self.timer_on.increase
                }
            ]
        }
        self.MENU_PLAY_1 = {
            "get_buffer": lambda: [0, Symbols.P, Symbols.L, Symbols.A, Symbols.Y, 0, Symbols.NUMBER[1], 0],
            "click": lambda: self.play_music(self.music.get_default_tracks())
        }
        self.MENU_VOLUME = {
            "group": "volume",
            "get_buffer": lambda: [0, Symbols.U, Symbols.O, Symbols.L, Symbols.U, Symbols.M1, Symbols.M2, Symbols.E],
            "get_sub_menu": lambda: [
                {
                    "get_buffer": self.music.get_draw_volume,
                    "click_left": self.music.decrease_volume,
                    "click_right": self.music.increase_volume
                }
            ]
        }
        self.MENU_STYLE = {
            "group": "style",
            "get_buffer": lambda: [0, Symbols.S, Symbols.T1, Symbols.T2, Symbols.Y, Symbols.L, Symbols.E, 0],
            "get_sub_menu": lambda: list(map(lambda x: {
                "get_buffer": lambda: x["buffer"],
                "on_draw": lambda: self.music.set_preset(x["name"])
            }, self.music.get_presets()))
        }
        self.MENU_RUN_SH = {
            "get_buffer": lambda: [0, Symbols.R, Symbols.U, Symbols.N, 0, Symbols.S, Symbols.H, 0],
            "click": lambda: self.music.run_sh(),
            "click_animation": True
        }
        self.MENU_DEMO = {
            "get_buffer": lambda: [0, 0, Symbols.D, Symbols.E, Symbols.M1, Symbols.M2, Symbols.O, 0],
            "click": lambda: (self.menu.draw_sub_menu_animation(self.music.get_draw_equalizer_animation()),
                              self.menu.reset_sub_menu())
        }
        self.MENU_SYSTEM = {
            "get_buffer": lambda: [Symbols.S, Symbols.Y, Symbols.S, Symbols.T1, Symbols.T2, Symbols.E, Symbols.M1, Symbols.M2],
            "get_sub_menu": lambda: [
                self.MENU_REBOOT,
                self.MENU_HALT
            ]
        }
        self.MENU_REBOOT = {
            "get_buffer": lambda: [0, Symbols.R, Symbols.E, Symbols.B, Symbols.O, Symbols.O, Symbols.T1, Symbols.T2],
            "click": lambda: self.music.reboot(),
            "click_animation": True
        }
        self.MENU_HALT = {
            "get_buffer": lambda: [0, 0, Symbols.H, Symbols.A, Symbols.L, Symbols.T1, Symbols.T2, 0],
            "click": lambda: self.music.halt(),
            "click_animation": True
        }

    def _on_menu_click(self):
        self.menu.click()

    def _on_menu_click_left(self):
        if (self.menu.is_sub_menu_visible()):
            self.menu.click_left()
        else:
            self._decrease_timer()

    def _on_menu_click_right(self):
        if (self.menu.is_sub_menu_visible()):
            self.menu.click_right()
        else:
            self._increase_timer()

    def _on_light_sensor_sudden_change(self, now, is_dark):
        if (self.music.is_playing()):
            if (now.hour >= self.config['light_sensor_time_from'] or now.hour < self.config['light_sensor_time_to']):
                if (is_dark):
                    if (self.music.get_volume() > self.config['light_sensor_volume']):
                        self.music.set_volume(self.config['light_sensor_volume'])
                    self.music.set_preset(self.config['light_sensor_preset'])
                    self.timer_off.reset()
                    self.timer_off.increase()
                    self.timer_off.increase()
                    self.timer_off.increase()
                    self.timer_off.increase()
                    self.menu.draw_sub_menu_animation(self.light_sensor.get_draw_sleep_animation())
                else:
                    self.timer_off.reset()
        else:
            if (is_dark):
                self.led.set_random_color()
            else:
                self.led.set_none_color()

    def _on_light_sensor_sudden_change_timeout(self):
        if (not self.music.is_playing()):
            self.led.set_none_color()

    def _on_change_preset(self, value):
        self.music.set_preset(value)
        if (value < 0):
            self.menu.click_left(self.MENU_STYLE)
        else:
            self.menu.click_right(self.MENU_STYLE)

    def _increase_timer(self):
        if (self.music.is_playing()):
            self.timer_off.increase()
            self.menu.draw_sub_menu(self.MENU_TIMER_OFF)
        else:
            self.timer_on.increase()
            self.menu.draw_sub_menu(self.MENU_TIMER_ON)

    def _decrease_timer(self):
        if (self.music.is_playing()):
            self.timer_off.decrease()
            self.menu.draw_sub_menu(self.MENU_TIMER_OFF)
        else:
            self.timer_on.decrease()
            self.menu.draw_sub_menu(self.MENU_TIMER_ON)

    def set_led_color(self, red, green, blue):
        self.led.set_color(red, green, blue)

    def run_alert(self):
        self.menu.draw_sub_menu_animation(self.alert.get_draw_alert_animation())
        self.alert.run()

    def get_presets(self):
        return self.music.get_presets()

    def set_preset(self, value):
        self.music.set_preset(value)

    def get_volume(self):
        return self.music.get_volume()

    def set_volume(self, volume):
        self.music.set_volume(volume)

    def get_state(self):
        return self.music.get_state()

    def play_stop_music(self):
        if (self.music.is_playing()):
            self.stop_music()
        else:
            self.play_music()

    def play_music(self, tracks=None):
        self.music.set_volume(self.config['default_volume'])
        self.music.set_preset(self.config['default_preset'])
        self.music.play(tracks)
        self.on_started()

    def pause_music(self):
        self.music.pause()
        self.on_paused()

    def stop_music(self):
        self.music.stop()
        self.on_stopped()

    def on_started(self):
        self.menu.draw_sub_menu_animation(self.music.get_draw_start_animation())

    def on_stopped(self):
        self.menu.draw_sub_menu_animation(self.music.get_draw_stop_animation())
        self.timer_off.reset()
        self.ir_sender.power(False)
        self.led.set_none_color()

    def on_playing(self):
        self.menu.draw_sub_menu_animation(self.music.get_draw_play_animation())
        self.timer_on.reset()
        self.led.set_random_color()

        if (self.music.is_playing()):
            self.ir_sender.power(True)

    def on_paused(self):
        self.menu.draw_sub_menu_animation(self.music.get_draw_pause_animation())

    def on_seeked(self):
        self.menu.draw_sub_menu_animation(self.music.get_draw_seek_animation())

    def on_mute(self, mute):
        if mute:
            self.on_volume_changed(0)
        else:
            self.on_volume_changed()

    def on_new_track_playing(self):
        self.led.set_random_color()

    def on_volume_changed(self, volume=None):
        if (self.menu is not None and self.music is not None and self.music.is_volume_changed(volume)):
            self.menu.draw_sub_menu(self.MENU_VOLUME)

    def on_playback_state_changed(self, old_state, new_state):
        if (old_state != new_state):
            if (self.music.is_playing(new_state)):
                self.on_playing()
            elif (self.music.is_paused(new_state)):
                self.on_paused()
