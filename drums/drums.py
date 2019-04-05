import abc

import matplotlib.pyplot as plt
import numpy as np
import simpleaudio as sa


SAMPLE_RATE = 44100
BIT_DEPTH = 16
DRUM_END_PADDING_SAMPLES = 10


class Drum(abc.ABC):
    SAMPLE_DURATION = 1
    T = np.linspace(0, SAMPLE_DURATION, SAMPLE_DURATION * SAMPLE_RATE, False)

    def __init__(self):
        self.sample = self.generate_sample()
        self.T = self._generate_timescale()
        self.play_object = None

    def play(self):
        self.play_object = sa.play_buffer(self.sample, 1, 2, SAMPLE_RATE)

    def stop(self):
        if self.play_object and self.play_object.is_playing():
            self.play_object.stop()

    @abc.abstractmethod
    def generate_sample(self):
        pass

    @classmethod
    def _generate_timescale(cls):
        return np.linspace(0, cls.SAMPLE_DURATION, cls.SAMPLE_DURATION * SAMPLE_RATE, False)

    def _linear_decay_envelope(self, max_value, min_value, decay_time):
        decay_end_point = int(decay_time * SAMPLE_RATE)
        decay_gradient = (min_value - max_value) / decay_time
        decay_segment = (self.T * decay_gradient + max_value)[:decay_end_point]
        sustain_segment = np.repeat(min_value, len(self.T[decay_end_point:]))
        return np.hstack([decay_segment, sustain_segment])

    def _tone_drum_synth(self, start_pitch, end_pitch, amp_decay_time, freq_decay_time):
        pitch_envelope = self._linear_decay_envelope(start_pitch, end_pitch, freq_decay_time)
        amp_envelope = self._linear_decay_envelope(1, 0, amp_decay_time)
        return self._normalise(amp_envelope * np.sin(self.T * 2 * np.pi * pitch_envelope))

    def _noise_drum_synth(self, amp_decay_time):
        amp_envelope = self._linear_decay_envelope(1, 0, amp_decay_time)
        return self._normalise(amp_envelope * np.random.uniform(size=len(self.T)))

    @staticmethod
    def _drum_end_index(amp_decay_time):
        return int(amp_decay_time * SAMPLE_RATE) + DRUM_END_PADDING_SAMPLES

    @staticmethod
    def _normalise(audio):
        max_range = 2 ** (BIT_DEPTH - 1) - 1
        return (audio * max_range / np.max(np.abs(audio))).astype(np.int16)


class BassDrum(Drum):
    def generate_sample(self):
        return self._tone_drum_synth(200, 40, 0.2, 0.25)


class SnareDrum(Drum):
    NOISE_VOLUME_RATIO = 0.5

    def generate_sample(self):
        tone_component = self._tone_drum_synth(500, 200, 0.1, 0.15)
        noise_component = self._noise_drum_synth(0.2)
        return self._normalise(
            tone_component * (1 - self.NOISE_VOLUME_RATIO) + noise_component * self.NOISE_VOLUME_RATIO
        )


class HighHat(Drum):
    def generate_sample(self):
        return self._noise_drum_synth(0.05)


if __name__ == '__main__':
    play = False
    visualise = True
    if play:
        import time
        bass_drum = BassDrum()
        snare_drum = SnareDrum()
        high_hat = HighHat()
        sleep_amount = 0.2
        while True:
            bass_drum.play()
            time.sleep(sleep_amount)
            high_hat.play()
            time.sleep(sleep_amount)
            snare_drum.play()
            time.sleep(sleep_amount)
            high_hat.play()
            time.sleep(sleep_amount)
    if visualise:
        print('Why does the kick drum make a plop sound?')
        bd = BassDrum()
        plt.plot(bd.T, bd.sample)
        plt.show()