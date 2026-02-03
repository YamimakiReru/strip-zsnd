from wave_format import WaveFormatParser, WaveFormat
from util import ZsndLogMixin, ZsndError

import wave
import io
from abc import ABC, abstractmethod

class ZeroSoundPredicate(ABC):
    @abstractmethod
    def is_zero_sound_sample(self, frames_as_bytes: bytes, pos_in_bytes: int, threshold: float):
        pass

class WavChunk:
    def __init__(self, frames_as_bytes: bytes, wave_format: WaveFormat):
        self._frames_as_bytes = frames_as_bytes
        self._wave_foramt = wave_format

    def __len__(self):
        '''
        Returns the number of samples contained in this buffer
        '''
        return len(self._frames_as_bytes) // self._wave_foramt.get_bytes_per_sample()

    def count_leading_zeros(self, predicate: ZeroSoundPredicate) -> int:
        count = 0
        for i in range(0, len(self._frames_as_bytes), self._wave_foramt.get_bytes_per_sample()):
            if predicate.is_zero_sound_sample(self._frames_as_bytes, i):
                count += 1
            else:
                break
        return count

    def count_trailing_zeros(self, predicate: ZeroSoundPredicate) -> int:
        sample_width = self._wave_foramt.get_bytes_per_sample()

        count = 0
        i = len(self._frames_as_bytes) - sample_width
        while i >= 0 and predicate.is_zero_sound_sample(self._frames_as_bytes, i):
            count += 1
            i -= sample_width
        return count

    def iterate_inner_zero_runs(self, predicate: ZeroSoundPredicate, threshold: int):
        sample_width = self._wave_foramt.get_bytes_per_sample()

        # skip leading and trailing zeros
        i = self.count_leading_zeros(predicate) * sample_width

        # scan inner dropouts
        num_bytes = len(self._frames_as_bytes)
        zero_run_length = 0
        zero_run_start = None
        while i < num_bytes:
            if predicate.is_zero_sound_sample(self._frames_as_bytes, i):
                if 0 == zero_run_length:
                    zero_run_start = i // sample_width
                zero_run_length += 1
            else:
                if zero_run_length > 0:
                    if zero_run_length >= threshold:
                        yield (zero_run_start, zero_run_length)
                    zero_run_length = 0
            i += sample_width

    def __getitem__(self, key):
        assert isinstance(key, slice) and key.start and key.stop
        sample_width = self._wave_foramt.get_bytes_per_sample()
        return self._frames_as_bytes[key.start * sample_width:
                key.end * sample_width]

class ZsndWavReader(ZsndLogMixin):
    def __init__(self, f: io.BufferedIOBase):
        logger = self.get_logger()

        try:
            self.wave_format = WaveFormatParser().parse(f)
            logger.debug(self.wave_format)
        except Exception as exc:
            raise ZsndError(_('zsnd.failed_to_detect_file_type') + str(exc)) from exc

        f.seek(0)

        self._wave_read: wave.Wave_read = wave.open(f)
        self.get_logger().debug(self._wave_read.getparams())
        if 2 <= self._wave_read.getnchannels():
            self._wave_read.close()
            raise ZsndError(_('zsnd.mono_only_supported'))

    def close(self):
        self._wave_read.close()

    def read(self, num_frames: int) -> WavChunk:
        frames_as_bytes = self._wave_read.readframes(num_frames)
        return WavChunk(frames_as_bytes, self.wave_format)

    def count_frames(self) -> int:
        """
        Return the number of frames.
        Each frame consists of one sample from every channel.
        """
        return self._wave_read.getnframes()

class ZsndWavWriter:
    def __init__(self, f: io.BufferedIOBase, reader: ZsndWavReader):
        self._wave_write: wave.Wave_write = wave.open(f, 'wb')
        self._wave_write.setnchannels(1)
        self._wave_write.setsampwidth(reader.wave_format.get_bytes_per_sample())
        self._wave_write.setframerate(reader.wave_format.nSamplesPerSec)

    def write(self, data: bytes):
        self._wave_write.writeframes(data)

    def close(self):
        self._wave_write.close()

    def tell(self):
        return self._wave_write.tell()
