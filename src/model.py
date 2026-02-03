# coding: utf-8
from __future__ import annotations

from r_framework import LogMixin

import wave
import struct
import io
from i18n import t as _
from abc import ABC, abstractmethod
from dataclasses import dataclass

class ZsndLogMixin(LogMixin):
    LOGGER_PRFIX = 'zsnd.'

class ZeroSoundPredicate(ABC):
#     def __init__(self, sample_width_in_bytes: int):
#         self.sample_width_in_bytes = sample_width_in_bytes

    @abstractmethod
    def is_zero_sound_sample(self, frames_as_bytes: bytes, pos: int):
        pass

# class IntZeroSamplePredicate(ZeroSamplePredicate):
#     DEFAULT_EPS = 1

#     def __init__(self, sample_width_in_bytes: int, eps: int = DEFAULT_EPS):
#         super().__init__(sample_width_in_bytes)
#         if eps is None:
#             self._eps = self.DEFAULT_EPS
#         else:
#             self._eps = int(eps)

#     def is_zero_sample(self, frames_as_bytes, pos):
#         # positive integer
#         if self._eps >= frames_as_bytes[pos]:
#             for i in range(1, self.sample_width_in_bytes):
#                 if 0 != frames_as_bytes[pos+i]:
#                     return False
#             return True
#         # negative integer
#         if self._eps >= (0x100 - frames_as_bytes[pos]):
#             for i in range(1, self.sample_width_in_bytes):
#                 if 0xFF != frames_as_bytes[pos+i]:
#                     return False
#             return True
#         return False

# class FloatZeroSamplePredicate(ZeroSamplePredicate):
#     DEFAULT_EPS = 1e-9

#     def __init__(self, sample_width_in_bytes: int, eps: float = DEFAULT_EPS):
#         super().__init__(sample_width_in_bytes)
#         if eps is None:
#             self._eps = self.DEFAULT_EPS
#         else:
#             self._eps = eps
#         match sample_width_in_bytes:
#             case 4:
#                 self._unpacker = struct.Struct('<f')
#             case 8:
#                 self._unpacker = struct.Struct('<d')
#             case _:
#                 raise RAudioException('Unsupported float format')

#     def is_zero_sample(self, frames_as_bytes, pos):
#         sliced = frames_as_bytes[pos:(pos+self.sample_width_in_bytes)]
#         fp = self._unpacker.unpack(sliced)[0]
#         return self._eps >= abs(fp)

class WavChunk:
    def __init__(self, frames_as_bytes: bytes, wave_format: WaveFormat):
        self._frames_as_bytes = frames_as_bytes
        self.wave_foramt = wave_format

    def __len__(self):
        '''
        Returns the number of samples contained in this buffer
        '''
        return len(self._frames_as_bytes) // self.wave_foramt.get_bytes_per_sample()

    def count_leading_zeros(self, predicate: ZeroSoundPredicate) -> int:
        count = 0
        for i in range(0, len(self._frames_as_bytes), self.wave_foramt.get_bytes_per_sample()):
            if predicate.is_zero_sound_sample(self._frames_as_bytes, i):
                count += 1
            else:
                break
        return count

    def count_trailing_zeros(self, predicate: ZeroSoundPredicate) -> int:
        sample_width = self.wave_foramt.get_bytes_per_sample()

        count = 0
        i = len(self._frames_as_bytes) - sample_width
        while i >= 0 and predicate.is_zero_sound_sample(self._frames_as_bytes, i):
            count += 1
            i -= sample_width
        return count

    def iterate_inner_zero_runs(self, predicate: ZeroSoundPredicate, threshold: int):
        sample_width = self.wave_foramt.get_bytes_per_sample()

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
        sample_width = self.wave_foramt.get_bytes_per_sample()
        return self._frames_as_bytes[key.start * sample_width:
                key.end * sample_width]

class RWavReader(ZsndLogMixin):
    def __init__(self, f: io.BufferedIOBase):
        logger = self.get_logger()

        self.wave_format = WaveFormatParser().parse(f)
        logger.debug(self.wave_format)

        f.seek(0)

        self._wave_read: wave.Wave_read = wave.open(f)
        self.get_logger().debug(self._wave_read.getparams())
        if 2 <= self._wave_read.getnchannels():
            self._wave_read.close()
            raise RAudioException(_('r.error.mono_only_supported'))

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

class RWavWriter:
    def __init__(self, f: io.BufferedIOBase, reader: RWavReader):
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

@dataclass
class WaveFormat:
    """
    See Also: https://learn.microsoft.com/ja-jp/windows/win32/api/mmeapi/ns-mmeapi-waveformatex
    """
    FORMAT_TAG_PCM          = 0x0001
    FORMAT_TAG_FLOAT        = 0x0003
    FORMAT_TAG_EXTENSIBLE   = 0xFFFE
    KSDATAFORMAT_SUBTYPE_PCM = bytes.fromhex(
            '01000000 0000 0010 8000 00AA00389B71'.replace(' ', ''))
    KSDATAFORMAT_SUBTYPE_IEEE_FLOAT = bytes.fromhex(
            '03000000 0000 0010 8000 00AA00389B71'.replace(' ', ''))

    wFormatTag: int
    nChannels: int
    nSamplesPerSec: int
    nAvgBytesPerSec: int
    nBlockAlign: int
    wBitsPerSample: int
    wValidBitsPerSample: int|None
    dwChannelMask: int|None
    SubFormat: bytes|None # GUID

    def get_bytes_per_sample(self) -> int:
        return (self.wBitsPerSample + 7) // 8

    def is_pcm(self):
        if self.wFormatTag == self.FORMAT_TAG_PCM:
            return True
        if self.wFormatTag == self.FORMAT_TAG_EXTENSIBLE:
            return self.SubFormat == self.KSDATAFORMAT_SUBTYPE_PCM
        return False
    
    def is_float(self):
        if self.wFormatTag == self.FORMAT_TAG_FLOAT:
            return True
        if self.wFormatTag == self.FORMAT_TAG_EXTENSIBLE:
            return self.SubFormat == self.KSDATAFORMAT_SUBTYPE_IEEE_FLOAT
        return False

class WaveFormatParser:
    def parse(self, f: io.BufferedIOBase):
        if not hasattr(f, 'readable') or not f.readable():
            raise RAudioException('passed stream is not readable')
        try:
            magic_riff, size, magic_wave = struct.unpack('<4sI4s', f.read(12))
            if b'RIFF' != magic_riff or b'WAVE' != magic_wave:
                RAudioException(_('r.error.unsupported_format_exc') % 'magic bytes not found')
            while True:
                header = f.read(8)
                if len(header) < 8:
                        RAudioException(_('r.error.unsupported_format_exc') % 'fmt chunk not found')
                chunk_id, chunk_size = struct.unpack('<4sI', header)
                if chunk_id == b'fmt ':
                    fmt_chunk = f.read(chunk_size)
                    return self._parse_fmt_chunk(fmt_chunk)
                else:
                    f.seek(chunk_size, 1)
        except RAudioException as exc:
            raise
        except Exception as exc:
            raise RAudioException(_('r.error.unsupported_format_exc') % str(exc)) from exc

    def _parse_fmt_chunk(self, fmt_chunk: bytes):
        wFormatTag, nChannels, nSamplesPerSec, nAvgBytesPerSec, \
        nBlockAlign, wBitsPerSample = struct.unpack('<HHIIHH', fmt_chunk[:16])
        wValidBitsPerSample = dwChannelMask = SubFormat = None
        if WaveFormat.FORMAT_TAG_EXTENSIBLE == wFormatTag:
            wValidBitsPerSample, dwChannelMask, SubFormat = \
                    struct.unpack('<HI16s', fmt_chunk[18:40])
        return WaveFormat(wFormatTag, nChannels, nSamplesPerSec, nAvgBytesPerSec, \
                nBlockAlign, wBitsPerSample,
                wValidBitsPerSample, dwChannelMask, SubFormat)

class RAudioException(Exception):
    pass
