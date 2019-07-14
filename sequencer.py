from itertools import cycle
import time
from typing import Dict
from typing import List

from drums import BassDrum
from drums import Drum
from drums import HighHat
from drums import SnareDrum
from sequencer_gui_interface import ListenerThread


class Sequencer:
    DEFAULT_PARAMS = {
        'pulses_per_beat': 4,
        'bpm': 120,
    }

    # Attributes that can be altered via the GUI
    PARAM_NAMES = [
        'pulses_per_beat',
        'bpm',
    ]

    def __repr__(self):
        return f'Sequencer {id(self)}'

    def __init__(self, pattern: Dict[Drum, List[bool]], **kwargs):
        self.sequencer_gui_interface = kwargs.pop('sequencer_gui_interface', None)

        self.params = {
            'playing': False,
            'pattern': pattern,
            **{param: kwargs.pop(param, self.DEFAULT_PARAMS[param]) for param in self.PARAM_NAMES},
        }

        self.drum_patterns = {
            drum(**kwargs): cycle(drum_pattern) for drum, drum_pattern in pattern.items()
        }

        # Start listening for messages from GUI
        if self.sequencer_gui_interface:
            ListenerThread(listener=self, getter_func=self.sequencer_gui_interface.get_from_sequencer_events_queue).start()

    def _calculate_pulse_duration(self):
        return 60 / (int(self.params['bpm']) * int(self.params['pulses_per_beat']))

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
        self.params['playing'] = not self.params['playing']
        while self.params['playing']:
            pulse_start_time = time.time()
            self._play_pulse()
            self._wait_pulse_done(pulse_start_time)

    play = play_or_stop


if __name__ == '__main__':
    sequencer = Sequencer(
        pattern={
            BassDrum: [
                1, 0, 0, 0,
                0, 0, 0, 0,
                1, 0, 1, 0,
                0, 0, 0, 0,
            ],
            SnareDrum: [
                0, 0, 0, 0,
                1, 0, 0, 0,
            ],
            HighHat: [1, 0, 1, 0, 1],
        },
    )
    sequencer.play()
