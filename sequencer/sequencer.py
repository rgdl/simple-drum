from itertools import cycle
import time


class Sequencer:
    pulses_per_beat = 2
    MAX_PULSES = 1000

    def __init__(self, pattern, bpm):
        self.pattern = pattern
        self.drum_patterns = {
            drum(): cycle(drum_pattern) for drum, drum_pattern in pattern.items()
        }

        self.pulse_duration = self._calculate_pulse_duration(bpm)
        self.playing = False

        self.pulse_count = 0

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
        t0 = time.time()
        while self.playing:
            pulse_start_time = time.time()
            self.pulse_count += 1
            self._play_pulse()
            self._wait_pulse_done(pulse_start_time)
            if self.pulse_count >= self.MAX_PULSES:
                self.playing = False
        print(
            ((time.time() - t0) / self.pulse_count) / self.pulse_duration
        )

    def stop(self):
        self.playing = False
