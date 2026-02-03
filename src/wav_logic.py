from wav_io import ZeroSoundPredicate

import struct
from typing import override

class _ZeroSoundPredicateImpl(ZeroSoundPredicate):
    def __init__(self, sample_width_in_bytes: int):
        assert 0 < sample_width_in_bytes
        self.sample_width_in_bytes = sample_width_in_bytes

    @staticmethod
    def db_to_amplitude(volume_in_db: float) -> float:
        assert 0 > volume_in_db
        # dBFS conversion:
        #   -6 dB  = 0.5x amplitude
        #   -20 dB = 0.1x amplitude
        amp = 10 ** (volume_in_db / 20)
        assert 0 < amp
        return amp
        # return the clamped value
        # return max(min(amp, 1.0), -1.0)

class _PcmIntZeroSoundPredicate(_ZeroSoundPredicateImpl):
    def __init__(self, sample_width_in_bytes, threshold_in_db: float):
        super().__init__(sample_width_in_bytes)
        normalized_amp = self.db_to_amplitude(threshold_in_db)
        # e.g., 32767 for 16-bit
        max_amp = (1 << (self.sample_width_in_bytes * 8 - 1)) - 1 
        amp = int(round(normalized_amp * max_amp))
        # is_zero_sound_sample() assumes the threshold <= 0xFF.
        amp = min(amp, 0xFF)
        self._positive_threshold = amp
        self._negative_threshold = 0x100 - amp # two's complement

    @classmethod
    def db_to_amplitude_for(cls, volume_in_db):
        return super().db_to_amplitude(volume_in_db)

    @override
    def is_zero_sound_sample(self, frames_as_bytes, pos_in_bytes):
        # positive integer
        if self._positive_threshold >= frames_as_bytes[pos_in_bytes]:
            if self._are_upper_bytes(0, frames_as_bytes, pos_in_bytes):
                return True
        # negative integer
        if self._negative_threshold <= frames_as_bytes[pos_in_bytes]:
            return self._are_upper_bytes(0xFF, frames_as_bytes, pos_in_bytes)
        return False

    def _are_upper_bytes(self, expected, frames_as_bytes, pos_in_bytes):
        for i in range(1, self.sample_width_in_bytes):
            if expected != frames_as_bytes[i + pos_in_bytes]:
                return False
        return True

class _PcmInt8ZeroSoundPredicate(_ZeroSoundPredicateImpl):
    '''
    8-bit PCM: unsigned (0–0xFF), 0x80 = center
    '''
    def __init__(self, threshold_in_db: float):
        super().__init__(1)
        normalized_amp = self.db_to_amplitude(threshold_in_db)
        amp = int(round(normalized_amp * 127))
        amp = min(amp, 0x7F)
        self._min_amp = 0x80 - amp
        self._max_amp = 0x80 + amp

    @override
    def is_zero_sound_sample(self, frames_as_bytes, pos_in_bytes):
        return self._min_amp \
                <= frames_as_bytes[pos_in_bytes] \
                <= self._max_amp

class _FloatZeroSoundPredicate(_ZeroSoundPredicateImpl):
    '''
    Float PCM: -1.0 < x < 1.0 (normalized)
    '''
    def __init__(self, sample_width_in_bytes, threshold_in_db: float):
        super().__init__(sample_width_in_bytes)
        match self.sample_width_in_bytes:
            case 4:
                self._unpacker = struct.Struct('<f')
            case 8:
                self._unpacker = struct.Struct('<d')
            case _:
                raise ZsndError('Unsupported float PCM format')
        self._max_amp = self.db_to_amplitude(threshold_in_db)
        self._min_amp = -self._max_amp

    @override
    def is_zero_sound_sample(self, frames_as_bytes, pos_in_bytes):
        end = pos_in_bytes + self.sample_width_in_bytes
        sliced = frames_as_bytes[pos_in_bytes:end]
        fp = self._unpacker.unpack(sliced)[0]
        return self._min_amp <= fp <= self._max_amp
