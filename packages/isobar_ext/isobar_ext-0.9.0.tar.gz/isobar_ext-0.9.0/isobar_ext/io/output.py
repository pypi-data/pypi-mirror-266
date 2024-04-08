import itertools
import logging

log = logging.getLogger(__name__)


class OutputDevice:
    def __init__(self):
        self.added_latency_seconds = 0.0

    @property
    def ticks_per_beat(self):
        return None

    def tick(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def note_on(self, note=60, velocity=64, channel=0, track_idx=0):
        pass

    def note_off(self, note=60, channel=0, track_idx=0):
        pass

    def all_notes_off(self):
        for channel, note_index in itertools.product(range(16), range(128)):
            self.note_off(note_index, channel=channel)

    def control(self, control=0, value=0, channel=0, track_idx=0):
        pass

    def program_change(self, program=0, channel=0, track_idx=0):
        pass

    def create(self, patch_spec, patch_params, output=None):
        pass
