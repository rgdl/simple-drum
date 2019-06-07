from itertools import cycle
import time
from typing import Dict
from typing import List
from typing import Union

from drums import Drum


class Sequencer:
    pulses_per_beat = 2

    def __init__(self, pattern: Dict[Drum, List[bool]], bpm: Union[int, float], **kwargs):
        self.pattern = pattern
        self.drum_patterns = {
            drum(**kwargs): cycle(drum_pattern) for drum, drum_pattern in pattern.items()
        }

        self.pulse_duration = self._calculate_pulse_duration(bpm)
        self.playing = False

    def _calculate_pulse_duration(self, bpm):
        return 60 / (bpm * self.pulses_per_beat)

    def _play_pulse(self):
        for drum, drum_pattern in self.drum_patterns.items():
            if next(drum_pattern):
                drum.play()

    def _wait_pulse_done(self, cycle_start_time):
        while time.time() - cycle_start_time <= self.pulse_duration:
            continue

    def play(self):
        self.playing = True
        while self.playing:
            pulse_start_time = time.time()
            self._play_pulse()
            self._wait_pulse_done(pulse_start_time)

    def stop(self):
        self.playing = False
