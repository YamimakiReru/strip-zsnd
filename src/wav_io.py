from wave_format import WaveFormatParser, WaveFormat
from util import ZsndLogMixin, ZsndError

import wave
import io
from abc import ABC, abstractmethod

class ZeroSoundPredicate(ABC):
    @abstractmethod
    def is_zero_sound_sample(self, frames_as_bytes: bytes, pos_in_bytes: int):
        pass

class ZsndWavChunk:
    def __init__(self, frames_as_bytes: bytes, bytes_per_sample: int):
        self._frames_as_bytes = frames_as_bytes
        self._bytes_per_sample = bytes_per_sample

    def __len__(self):
        '''
        Returns the number of samples contained in this buffer
        '''
        return len(self._frames_as_bytes) // self._bytes_per_sample

    def count_leading_zeros(self, predicate: ZeroSoundPredicate) -> int:
        count = 0
        for i in range(0, len(self._frames_as_bytes), self._bytes_per_sample):
            if predicate.is_zero_sound_sample(self._frames_as_bytes, i):
                count += 1
            else:
                break
        return count

    def count_trailing_zeros(self, predicate: ZeroSoundPredicate) -> int:
        count = 0
        i = len(self._frames_as_bytes) - self._bytes_per_sample
        while i >= 0 and predicate.is_zero_sound_sample(self._frames_as_bytes, i):
            count += 1
            i -= self._bytes_per_sample
        return count

    def iterate_inner_zero_runs(self, predicate: ZeroSoundPredicate):
        # skip leading and trailing zeros
        i = self.count_leading_zeros(predicate) * self._bytes_per_sample

        # scan inner dropouts
        num_bytes = len(self._frames_as_bytes)
        zero_run_length = 0
        zero_run_start = None
        while i < num_bytes:
            if predicate.is_zero_sound_sample(self._frames_as_bytes, i):
                if 0 == zero_run_length:
                    zero_run_start = i // self._bytes_per_sample
                zero_run_length += 1
            else:
                if zero_run_length > 0:
                    yield (zero_run_start, zero_run_length)
                    zero_run_length = 0
            i += self._bytes_per_sample

    def __getitem__(self, key):
        assert isinstance(key, slice) and key.start and key.stop
        return self._frames_as_bytes[key.start * self._bytes_per_sample
                : key.end * self._bytes_per_sample]

class ZsndWavReader(ZsndLogMixin):
    def __init__(self, f: io.BufferedIOBase):
        logger = self.get_logger()

        try:
            self._wave_format = WaveFormatParser().parse(f)
            logger.debug(self._wave_format)
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

    def read(self, num_frames: int) -> ZsndWavChunk:
        frames_as_bytes = self._wave_read.readframes(num_frames)
        return ZsndWavChunk(frames_as_bytes, self._wave_format.get_bytes_per_sample())
    
    def tell(self):
        return self._wave_read.tell()

    def count_frames(self) -> int:
        """
        Return the number of frames.
        Each frame consists of one sample from every channel.
        """
        return self._wave_read.getnframes()
    
    def get_sample_rate(self) -> int:
        return self._wave_read.getframerate()
    
    def get_wave_format(self) -> WaveFormat:
        return self._wave_format

class ZsndWavWriter:
    def __init__(self, f: io.BufferedIOBase, bytes_per_sample: int, sample_rate: int):
        self._wave_write: wave.Wave_write = wave.open(f, 'wb')
        self._wave_write.setnchannels(1)
        self._wave_write.setsampwidth(bytes_per_sample)
        self._wave_write.setframerate(sample_rate)

    def write(self, data: bytes):
        self._wave_write.writeframes(data)

    def close(self):
        self._wave_write.close()

    def tell(self):
        return self._wave_write.tell()
