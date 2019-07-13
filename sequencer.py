from itertools import cycle
import time
from typing import Dict
from typing import List
from typing import Union

from drums import Drum
from sequencer_gui_interface import ListenerThread


class Sequencer:
    pulses_per_beat = 2

    def __repr__(self):
        return f'Sequencer {id(self)}'

    def __init__(self, pattern: Dict[Drum, List[bool]], bpm: Union[int, float], **kwargs):
        self.sequencer_gui_interface = kwargs.pop('sequencer_gui_interface', None)
        self.pattern = pattern
        self.bpm = bpm
        self.drum_patterns = {
            drum(**kwargs): cycle(drum_pattern) for drum, drum_pattern in pattern.items()
        }

        self.playing = False

        # Start listening for messages from GUI
        ListenerThread(listener=self, getter_func=self.sequencer_gui_interface.get_from_sequencer_events_queue).start()

    def _calculate_pulse_duration(self):
        return 60 / (int(self.bpm) * int(self.pulses_per_beat))

    def _play_pulse(self):
        for drum, drum_pattern in self.drum_patterns.items():
            if next(drum_pattern):
                drum.play()

    def _wait_pulse_done(self, cycle_start_time):
        pulse_duration = self._calculate_pulse_duration()
        while time.time() - cycle_start_time <= pulse_duration:
            continue

    def play_or_stop(self):
        print('called `play_or_stop`')
        self.playing = not self.playing
        while self.playing:
            pulse_start_time = time.time()
            self._play_pulse()
            self._wait_pulse_done(pulse_start_time)

    play = play_or_stop
    # def stop(self):
    #     self.playing = False
