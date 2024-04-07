from mopidy import core
from random import randint
import logging
import os
from subprocess import call
from .max7219 import Symbols


class Music:
    P = Symbols.P
    L = Symbols.L
    A = Symbols.A
    Y = Symbols.Y
    S = Symbols.S
    T1 = Symbols.T1
    T2 = Symbols.T2
    O = Symbols.O
    U = Symbols.U
    E = Symbols.E

    ANIMATION_PLAY = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, P],
            [0, 0, 0, 0, 0, 0, P, 0],
            [0, 0, 0, 0, 0, P, 0, 0],
            [0, 0, 0, 0, P, 0, 0, 0],
            [0, 0, 0, P, 0, 0, 0, 0],
            [0, 0, P, 0, 0, 0, 0, L],
            [0, 0, P, 0, 0, 0, L, 0],
            [0, 0, P, 0, 0, L, 0, 0],
            [0, 0, P, 0, L, 0, 0, 0],
            [0, 0, P, L, 0, 0, 0, A],
            [0, 0, P, L, 0, 0, A, 0],
            [0, 0, P, L, 0, A, 0, 0],
            [0, 0, P, L, A, 0, 0, Y],
            [0, 0, P, L, A, 0, Y, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, L, A, Y, 0, 0]
        ]
    }

    ANIMATION_STOP = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, S],
            [0, 0, 0, 0, 0, 0, S, 0],
            [0, 0, 0, 0, 0, S, 0, 0],
            [0, 0, 0, 0, S, 0, 0, 0],
            [0, 0, 0, S, 0, 0, 0, 0],
            [0, 0, S, 0, 0, 0, 0, T1],
            [0, 0, S, 0, 0, 0, T1, T2],
            [0, 0, S, 0, 0, T1, T2, 0],
            [0, 0, S, 0, T1, T2, 0, 0],
            [0, 0, S, T1, T2, 0, 0, O],
            [0, 0, S, T1, T2, 0, O, 0],
            [0, 0, S, T1, T2, O, 0, P],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, T1, T2, O, P, 0]
        ]
    }

    ANIMATION_PAUSE = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, P],
            [0, 0, 0, 0, 0, 0, P, 0],
            [0, 0, 0, 0, 0, P, 0, 0],
            [0, 0, 0, 0, P, 0, 0, 0],
            [0, 0, 0, P, 0, 0, 0, 0],
            [0, 0, P, 0, 0, 0, 0, A],
            [0, 0, P, 0, 0, 0, A, 0],
            [0, 0, P, 0, 0, A, 0, 0],
            [0, 0, P, 0, A, 0, 0, 0],
            [0, 0, P, A, 0, 0, 0, U],
            [0, 0, P, A, 0, 0, U, 0],
            [0, 0, P, A, 0, U, 0, 0],
            [0, 0, P, A, U, 0, 0, S],
            [0, 0, P, A, U, 0, S, 0],
            [0, 0, P, A, U, S, 0, E],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, A, U, S, E, 0]
        ]
    }

    BOTTOM = Symbols.BOTTOM
    TOP = Symbols.TOP
    LEFT_TOP = Symbols.LEFT_TOP
    LEFT_BOTTOM = Symbols.LEFT_BOTTOM
    RIGHT_TOP = Symbols.RIGHT_TOP
    RIGHT_BOTTOM = Symbols.RIGHT_BOTTOM

    ANIMATION_SPINNER = {
        "length": 1,
        "repeat": 3,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, BOTTOM],
            [0, 0, 0, 0, 0, 0, BOTTOM, 0],
            [0, 0, 0, 0, 0, BOTTOM, 0, 0],
            [0, 0, 0, 0, BOTTOM, 0, 0, 0],
            [0, 0, 0, BOTTOM, 0, 0, 0, 0],
            [0, 0, BOTTOM, 0, 0, 0, 0, 0],
            [0, BOTTOM, 0, 0, 0, 0, 0, 0],
            [BOTTOM, 0, 0, 0, 0, 0, 0, 0],
            [LEFT_BOTTOM, 0, 0, 0, 0, 0, 0, 0],
            [LEFT_TOP, 0, 0, 0, 0, 0, 0, 0],
            [TOP, 0, 0, 0, 0, 0, 0, 0],
            [0, TOP, 0, 0, 0, 0, 0, 0],
            [0, 0, TOP, 0, 0, 0, 0, 0],
            [0, 0, 0, TOP, 0, 0, 0, 0],
            [0, 0, 0, 0, TOP, 0, 0, 0],
            [0, 0, 0, 0, 0, TOP, 0, 0],
            [0, 0, 0, 0, 0, 0, TOP, 0],
            [0, 0, 0, 0, 0, 0, 0, TOP],
            [0, 0, 0, 0, 0, 0, 0, RIGHT_TOP],
            [0, 0, 0, 0, 0, 0, 0, RIGHT_BOTTOM]
        ]
    }

    MIDDLE = Symbols.MIDDLE

    ANIMATION_START = {
        "length": 5,
        "repeat": 20,
        "sleep": 0.02,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, MIDDLE],
            [0, 0, 0, 0, 0, 0, MIDDLE, 0],
            [0, 0, 0, 0, 0, MIDDLE, 0, 0],
            [0, 0, 0, 0, MIDDLE, 0, 0, 0],
            [0, 0, 0, MIDDLE, 0, 0, 0, 0],
            [0, 0, MIDDLE, 0, 0, 0, 0, 0],
            [0, MIDDLE, 0, 0, 0, 0, 0, 0],
            [MIDDLE, 0, 0, 0, 0, 0, 0, 0],
            [0, MIDDLE, 0, 0, 0, 0, 0, 0],
            [0, 0, MIDDLE, 0, 0, 0, 0, 0],
            [0, 0, 0, MIDDLE, 0, 0, 0, 0],
            [0, 0, 0, 0, MIDDLE, 0, 0, 0],
            [0, 0, 0, 0, 0, MIDDLE, 0, 0],
            [0, 0, 0, 0, 0, 0, MIDDLE, 0]
        ]
    }

    M0 = int('00000000', 2)
    M1 = int('00001000', 2)
    M2 = int('00001001', 2)
    M3 = int('01001001', 2)
    MUSIC_EQUALIZER = [M0, M1, M2, M3]

    N = Symbols.N
    B = Symbols.NUMBER[8]
    F = Symbols.F
    C = Symbols.C
    I = Symbols.I
    D = Symbols.D
    H = Symbols.H
    R = Symbols.R
    b = Symbols.B
    G = Symbols.NUMBER[6]

    PRESETS = [
        {"name": "flat", "curve": [65, 65, 65, 65, 65, 65, 65, 65, 65, 65], "buffer": [0, F, L, A, T1, T2, 0, 0]},
        {"name": "classical", "curve": [71, 71, 71, 71, 71, 71, 84, 83, 83, 87], "buffer": [C, L, A, S, S, I, C, 0]},
        {"name": "club", "curve": [71, 71, 67, 63, 63, 63, 67, 71, 71, 71], "buffer": [0, 0, C, L, U, B, 0, 0]},
        {"name": "dance", "curve": [57, 61, 69, 71, 71, 81, 83, 83, 71, 71], "buffer": [0, D, A, N, C, E, 0, 0]},
        {"name": "headphones", "curve": [65, 55, 64, 77, 75, 70, 65, 57, 52, 49], "buffer": [H, E, A, D, P, H, O, N]},
        {"name": "bass", "curve": [59, 59, 59, 63, 70, 78, 85, 88, 89, 89], "buffer": [0, 0, B, A, S, S, 0, 0]},
        {"name": "treble", "curve": [87, 87, 87, 78, 68, 55, 47, 47, 47, 45], "buffer": [T1, T2, R, E, b, L, E, 0]},
        {"name": "large_hall", "curve": [56, 56, 63, 63, 71, 79, 79, 79, 71, 71], "buffer": [0, 0, H, A, L, L, 0, 0]},
        {"name": "live", "curve": [79, 71, 66, 64, 63, 63, 66, 68, 68, 69], "buffer": [0, 0, L, I, U, E, 0, 0]},
        {"name": "party", "curve": [61, 61, 71, 71, 71, 71, 71, 71, 61, 61], "buffer": [0, P, A, R, T1, T2, Y, 0]},
        {"name": "pop", "curve": [74, 65, 61, 60, 64, 73, 75, 75, 74, 74], "buffer": [0, 0, P, O, P, 0, 0, 0]},
        {"name": "reggae", "curve": [71, 71, 72, 81, 71, 62, 62, 71, 71, 71], "buffer": [0, R, E, G, G, A, E, 0]},
        {"name": "rock", "curve": [58, 63, 80, 84, 77, 66, 58, 55, 55, 55], "buffer": [0, 0, R, O, C, H, 0, 0]},
        {"name": "ska", "curve": [75, 79, 78, 72, 66, 63, 58, 57, 55, 57], "buffer": [0, 0, S, H, A, 0, 0, 0]},
        {"name": "soft_rock", "curve": [66, 66, 69, 72, 78, 80, 77, 72, 68, 58], "buffer": [S, O, F, T2, R, O, C, H]},
        {"name": "soft", "curve": [65, 70, 73, 75, 73, 66, 59, 57, 55, 53], "buffer": [0, S, O, F, T1, T2, 0, 0]},
        {"name": "techno", "curve": [60, 63, 71, 80, 79, 71, 60, 57, 57, 58], "buffer": [T1, T2, E, C, H, N, O, 0]},
        {"name": "nobass3", "curve": [0, 4, 14, 23, 47, 70, 87, 87, 87, 88], "buffer": [N, O, 0, B, A, S, S, Symbols.NUMBER[3]]},
        {"name": "nobass2", "curve": [0, 4, 14, 23, 47, 67, 76, 76, 76, 76], "buffer": [N, O, 0, B, A, S, S, Symbols.NUMBER[2]]},
        {"name": "nobass", "curve": [0, 4, 14, 23, 47, 65, 65, 65, 65, 65], "buffer": [N, O, 0, B, A, S, S, 0]}
    ]

    def __init__(self, core, default_tracks, preset):
        self._core = core
        self._volume = self.get_volume(),
        self._default_tracks = list(default_tracks) if isinstance(default_tracks, tuple) else [default_tracks]
        self._preset = preset

    def is_playing(self, state=None):
        if (state is None):
            state = self.get_state()
        return state == core.PlaybackState.PLAYING

    def is_paused(self, state=None):
        if (state is None):
            state = self.get_state()
        return state == core.PlaybackState.PAUSED

    def is_stopped(self, state=None):
        if (state is None):
            state = self.get_state()
        return state == core.PlaybackState.STOPPED

    def is_volume_changed(self, volume):
        if (self._volume != volume):
            self._volume = volume
            return True
        else:
            return False

    def is_mute(self):
        return self._core.mixer.get_mute().get()

    def play(self, tracks):
        if (tracks is not None):
            self._core.playback.stop()
            self._core.tracklist.clear()
            self._core.tracklist.add(uris=tracks)
            self._core.tracklist.set_consume(False)
            self._core.tracklist.set_single(False)
            self._core.tracklist.set_repeat(True)
            self._core.tracklist.set_random(True)
        if (not self.is_playing()):
            if (self._core.tracklist.get_length().get() < 1):
                self._core.tracklist.add(uris=self._default_tracks)
                self._core.tracklist.set_repeat(True)
                self._core.tracklist.set_random(True)
            self._core.playback.play()

    def pause(self):
        if (not self.is_paused()):
            self._core.playback.pause()

    def stop(self):
        if (self.is_playing()):
            self._core.playback.stop()

    def reboot(self):
        try:
            call("sudo shutdown -r now", shell=True)
        except Exception as inst:
            logging.error(inst)

    def halt(self):
        try:
            call("sudo shutdown -h now", shell=True)
        except Exception as inst:
            logging.error(inst)

    def run_sh(self):
        try:
            call(["sh", os.path.join(os.path.dirname(__file__), "run.sh")])
        except Exception as inst:
            logging.error(inst)

    def mute(self):
        self._core.mixer.set_mute(not self.is_mute())

    def set_preset(self, value):
        index = 0
        if (value == -1 or value == 1):
            index = (self._get_preset_index(self._preset) + value + len(self.PRESETS)) % len(self.PRESETS)
        else:
            index = self._get_preset_index(value)

        self._preset = self.PRESETS[index]["name"]
        try:
            curve = ""
            for i, c in enumerate(self.PRESETS[index]["curve"]):
                curve += "echo cset numid=%d %d;" % (i + 1, c)
            call("{ %s } | amixer -D equal -s" % curve, shell=True)
        except Exception as inst:
            logging.error(inst)
        return self.PRESETS[index]["buffer"]

    def get_presets(self):
        index = self._get_preset_index(self._preset)
        return self.PRESETS[index:len(self.PRESETS)] + self.PRESETS[0:index]

    def _get_preset_index(self, name):
        for i, p in enumerate(self.PRESETS):
            if (p["name"] == name):
                return i
        return 0

    def get_state(self):
        return self._core.playback.get_state().get()

    def get_volume(self):
        return self._core.mixer.get_volume().get()

    def set_volume(self, volume):
        if (volume < 0):
            volume = 0
        elif (volume > 100):
            volume = 100
        self._core.mixer.set_volume(volume)

    def increase_volume(self, volume=1):
        self.set_volume(self.get_volume() + volume)

    def decrease_volume(self, volume=1):
        self.set_volume(self.get_volume() - volume)

    def get_default_tracks(self):
        return self._default_tracks

    def get_draw_start_animation(self):
        return self.ANIMATION_START

    def get_draw_play_animation(self):
        return self.ANIMATION_PLAY

    def get_draw_stop_animation(self):
        return self.ANIMATION_STOP

    def get_draw_pause_animation(self):
        return self.ANIMATION_PAUSE

    def get_draw_seek_animation(self):
        return self.ANIMATION_SPINNER

    def get_draw_equalizer_animation(self):
        animation = []

        for j in range(120):
            frame = []
            for i in range(8):
                if (j > 0):
                    index = self.MUSIC_EQUALIZER.index(animation[j - 1][i]) + randint(-1, 1)
                    if (index < 0):
                        index = 0
                    elif (index > 3):
                        index = 3
                    frame.append(self.MUSIC_EQUALIZER[index])
                else:
                    frame.append(self.MUSIC_EQUALIZER[randint(0, 3)])
            animation.append(frame)

        return {
            "length": 3600,
            "repeat": 720,
            "sleep": 0.05,
            "buffer": animation
        }

    def get_draw_volume(self, volume=None):
        if (volume is None):
            volume = self.get_volume()

        # if (self.is_mute()):
        #     volume = 0

        return [
            Symbols.U,
            Symbols.O,
            Symbols.L,
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE if volume < 100 else Symbols.NUMBER[int(volume / 100)],
            Symbols.NONE if volume < 10 else Symbols.NUMBER[int(volume / 10) % 10],
            Symbols.NUMBER[volume % 10]
        ]
