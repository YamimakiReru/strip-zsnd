from io import BufferedIOBase
import struct
from dataclasses import dataclass

class WaveFormatError(ValueError):
    pass

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
    wValidBitsPerSample: int|None = None
    dwChannelMask: int|None = None
    SubFormat: bytes|None = None # GUID

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
    def parse(self, f: BufferedIOBase):
        if not hasattr(f, 'readable') or not f.readable():
            raise WaveFormatError('passed stream is not readable')
        try:
            magic_riff, size, magic_wave = struct.unpack('<4sI4s', f.read(12))
            if b'RIFF' != magic_riff or b'WAVE' != magic_wave:
                raise WaveFormatError('magic bytes not found')
            while True:
                header = f.read(8)
                if len(header) < 8:
                        raise WaveFormatError('fmt chunk not found')
                chunk_id, chunk_size = struct.unpack('<4sI', header)
                if chunk_id == b'fmt ':
                    fmt_chunk = f.read(chunk_size)
                    return self._parse_fmt_chunk(fmt_chunk)
                else:
                    f.seek(chunk_size, 1)
        except WaveFormatError as exc:
            raise
        except Exception as exc:
            raise WaveFormatError(str(exc)) from exc

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
