import abc
import re
import warnings

import matplotlib.pyplot as plt
import numpy as np
import simpleaudio as sa


SAMPLE_RATE = 44100
BIT_DEPTH = 16
DRUM_END_PADDING_SAMPLES = 10


class Drum(abc.ABC):
    SAMPLE_DURATION = 1
    T = np.linspace(0, SAMPLE_DURATION, SAMPLE_DURATION * SAMPLE_RATE, False)
    DT = T[1] - T[0]

    PARAMETER_RANGE_LOOKUP = {
        '^.*DECAY$': (1e-3, SAMPLE_DURATION),
        '^.*PITCH$': (2e1, 2e3),
        '^.*RATIO$': (0, 1),
    }

    def __init__(self, **init_params):
        self.params = self.DEFAULT_PARAMS
        if init_params:
            unrecognised_parameters = set(init_params.keys()) - set(self.DEFAULT_PARAMS.keys())
            if unrecognised_parameters:
                raise TypeError(f'Unrecognised parameters supplied: {unrecognised_parameters}')
            self.params.update(init_params)

        self.parameter_ranges = {param: self._get_parameter_valid_range(param) for param in self.params.keys()}
        self._validate_params()

        self.envelopes = {}
        self.sample = None

        self.update_sample()
        self.play_object = None

    def play(self):
        self.play_object = sa.play_buffer(self.sample, 1, 2, SAMPLE_RATE)

    def stop(self):
        if self.play_object and self.play_object.is_playing():
            self.play_object.stop()

    @abc.abstractmethod
    def generate_sample(self):
        pass

    def update_sample(self, params={}):
        if params:
            self.params.update(params)
        self.sample = self.generate_sample()

    def _get_parameter_valid_range(self, parameter_name):
        for pattern, valid_range in self.PARAMETER_RANGE_LOOKUP.items():
            if re.match(pattern, parameter_name):
                return valid_range

    def _validate_params(self):
        for name, value in self.params.items():
            valid_range = self.parameter_ranges[name]
            if not valid_range:
                warnings.warn(f'No range validation for parameter {name}')
                return
            if not valid_range[0] <= value <= valid_range[1]:
                raise ValueError(f'{self.__class__.__name__} {name} = {value}, must be in the range {valid_range}')

    def _decay_envelope(self, max_value, min_value, decay_time):
        decay_end_point = int(decay_time * SAMPLE_RATE)
        decay_gradient = (min_value - max_value) / decay_time
        decay_segment = (self.T * decay_gradient + max_value)[:decay_end_point]
        sustain_segment = np.repeat(min_value, len(self.T[decay_end_point:]))
        return np.hstack([decay_segment, sustain_segment])

    def _tone_drum_synth(self, start_pitch, end_pitch, amp_decay_time, freq_decay_time):
        pitch_envelope = self._decay_envelope(start_pitch, end_pitch, freq_decay_time)
        amp_envelope = self._decay_envelope(1, 0, amp_decay_time)
        self.envelopes['tone_pitch_envelope'] = pitch_envelope
        self.envelopes['tone_amp_envelope'] = amp_envelope
        return self._normalise(amp_envelope * np.sin(2 * np.pi * pitch_envelope.cumsum() * self.DT))

    def _noise_drum_synth(self, amp_decay_time):
        amp_envelope = self._decay_envelope(1, 0, amp_decay_time)
        self.envelopes['noise_amp_envelope'] = amp_envelope
        return self._normalise(amp_envelope * np.random.uniform(size=len(self.T)))

    @staticmethod
    def _drum_end_index(amp_decay_time):
        return int(amp_decay_time * SAMPLE_RATE) + DRUM_END_PADDING_SAMPLES

    @staticmethod
    def _normalise(audio):
        max_range = 2 ** (BIT_DEPTH - 1) - 1
        return (audio * max_range / np.max(np.abs(audio))).astype(np.int16)


class BassDrum(Drum):
    DEFAULT_PARAMS = {
        'MAX_PITCH': 200,
        'MIN_PITCH': 40,
        'AMP_DECAY': 0.3,
        'FREQ_DECAY': 0.2,
    }

    def generate_sample(self):
        return self._tone_drum_synth(
            self.params['MAX_PITCH'],
            self.params['MIN_PITCH'],
            self.params['AMP_DECAY'],
            self.params['FREQ_DECAY'],
        )


class SnareDrum(Drum):
    DEFAULT_PARAMS = {
        'MAX_PITCH': 400,
        'MIN_PITCH': 200,
        'TONE_AMP_DECAY': 0.2,
        'FREQ_DECAY': 0.3,
        'NOISE_AMP_DECAY': 0.2,
        'NOISE_VOLUME_RATIO': 0.5,
    }

    def generate_sample(self):
        tone_component = self._tone_drum_synth(
            start_pitch=self.params['MAX_PITCH'],
            end_pitch=self.params['MIN_PITCH'],
            amp_decay_time=self.params['TONE_AMP_DECAY'],
            freq_decay_time=self.params['FREQ_DECAY'],
        )
        noise_component = self._noise_drum_synth(amp_decay_time=self.params['NOISE_AMP_DECAY'])
        return self._normalise(
            tone_component * (1 - self.params['NOISE_VOLUME_RATIO'])
            + noise_component * self.params['NOISE_VOLUME_RATIO']
        )


class HighHat(Drum):
    DEFAULT_PARAMS = {
        'DECAY': 0.03,
    }

    def generate_sample(self):
        return self._noise_drum_synth(self.params['DECAY'])


if __name__ == '__main__':
    play = True
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
        bd = BassDrum()
        plt.plot(bd.T, bd.sample)
        plt.show()
