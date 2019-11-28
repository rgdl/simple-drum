from itertools import cycle
import sys
from threading import Thread
import time
from typing import Dict
from typing import List

from drums import BassDrum
from drums import Drum
from drums import HighHat
from drums import SnareDrum
from sequencer_gui_interface import ListenerThread, GUIEvent


class Sequencer:
    # Excludes "special" params `is_playing` and `pattern`, which require some special handling
    BASIC_PARAM_NAMES = [
        'pulses_per_beat',
        'bpm',
    ]
    # All attributes that can be altered via the GUI
    PARAM_NAMES = BASIC_PARAM_NAMES + [
        'is_playing',
        'pattern',
    ]
    DEFAULT_PARAMS = {
        'pulses_per_beat': 4,
        'bpm': 120,
    }
    assert set(BASIC_PARAM_NAMES) == set(DEFAULT_PARAMS.keys())

    def __getattr__(self, attr):
        """
        If attr is of the form set_attr, return a lambda which sets self.attr to the value of a supplied dict of this 
        form: {attr: value}
        """
        try:
            split_attr = attr.split('_', 1)
            if split_attr[0] == 'set' and split_attr[1] in self.BASIC_PARAM_NAMES:
                def func(**kwargs):
                    self.params[split_attr[1]] = kwargs[split_attr[1]]
                return func
        except AttributeError:
            pass
        return super().__getattr__(attr)

    def __repr__(self):
        return 'Sequencer ' + str({k: self.params[k] for k in self.BASIC_PARAM_NAMES})

    def __init__(self, pattern: Dict[Drum, List[bool]], **kwargs):
        self.sequencer_gui_interface = kwargs.pop('sequencer_gui_interface', None)

        self.params = {
            'playing': False,
            'pattern': pattern,
            **{param: kwargs.pop(param, self.DEFAULT_PARAMS[param]) for param in self.BASIC_PARAM_NAMES},
        }

        self.drum_patterns = {
            drum(**kwargs): cycle(drum_pattern) for drum, drum_pattern in pattern.items()
        }

        # Start listening for messages from GUI
        if self.sequencer_gui_interface:
            self._push_initial_params_to_gui()
            ListenerThread(
                listener=self,
                getter_func=self.sequencer_gui_interface.get_from_sequencer_events_queue,
            ).start()

    def _calculate_pulse_duration(self):
        return 60 / (int(self.params['bpm']) * int(self.params['pulses_per_beat']))

    def _play_pulse(self):
        for drum, drum_pattern in self.drum_patterns.items():
            if next(drum_pattern):
                drum.play()

    def _push_initial_params_to_gui(self):
        self.sequencer_gui_interface.push_to_gui_events_queue(GUIEvent('initialise_params', self.params))

    def _wait_pulse_done(self, cycle_start_time):
        pulse_duration = self._calculate_pulse_duration()
        while time.time() - cycle_start_time <= pulse_duration:
            continue

    def play_pulse(self):
        pulse_start_time = time.time()
        self._play_pulse()
        self._wait_pulse_done(pulse_start_time)

    def play_or_stop(self):
        self.params['playing'] = not self.params['playing']
        if self.params['playing']:
            PlayThread(self).start()

    play = play_or_stop

    def quit(self):
        # TODO: this doesn't stop everything running
        self.params['playing'] = False
        sys.exit()


class PlayThread(Thread):
    def __init__(self, sequencer: Sequencer):
        super().__init__()
        self.sequencer = sequencer

    def run(self):
        while self.sequencer.params['playing']:
            self.sequencer.play_pulse()


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
