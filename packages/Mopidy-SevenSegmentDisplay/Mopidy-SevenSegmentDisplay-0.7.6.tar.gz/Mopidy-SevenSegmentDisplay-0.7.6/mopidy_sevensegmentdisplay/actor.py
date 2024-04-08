import pykka
import logging
from mopidy.core import CoreListener
from .worker import Worker


logger = logging.getLogger(__name__)


class Frontend(pykka.ThreadingActor, CoreListener):
    worker = Worker()

    def __init__(self, config, core):
        super().__init__()

        self.config = config['sevensegmentdisplay']
        self.core = core

    def on_start(self):
        logger.warning('started')
        self.worker.start(self.config, self.core)

    def on_stop(self):
        logger.warning('stopped')
        self.worker.stop()

    def on_failure(self, exception_type, exception_value, traceback):
        logger.warning('failing')
        self.worker.stop()

    def on_event(self, event, **kwargs):
        if (event == 'stream_title_changed'):
            self.worker.on_seeked()
        elif (event == 'track_playback_started'):
            self.worker.on_new_track_playing()
        return CoreListener.on_event(self, event, **kwargs)

    def playback_state_changed(self, old_state, new_state):
        self.worker.on_playback_state_changed(old_state, new_state)

    # def track_playback_started(self, tl_track):
    #     logger.warning('playback_started!')
    #     self.worker.on_playing()

    # def track_playback_paused(self, tl_track, time_position):
    #     logger.warning('playback_paused!')
    #     self.worker.on_paused()

    # def track_playback_resumed(self, tl_track, time_position):
    #     logger.warning('playback_resumed!')
    #     self.worker.on_playing()

    # def track_playback_ended(self, tl_track, time_position):
    #     logger.warning('playback_ended!')
    #     self.worker.on_stopped()

    def volume_changed(self, volume):
        self.worker.on_volume_changed(volume)

    def mute_changed(self, mute):
        self.worker.on_mute(mute)

    def seeked(self, time_position):
        self.worker.on_seeked()

    # def playlists_loaded(self):
    #     logger.warning('Received playlists_loaded event')

    # def playlist_changed(self, playlist):
    #     logger.warning('Received playlist_changed event')
