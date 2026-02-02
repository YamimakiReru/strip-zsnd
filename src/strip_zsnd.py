# coding: utf-8
# from __future__ import annotations

from r_framework import TyperApp

from pathlib import Path
# import wave
# from i18n import t as _
# import struct
# import argparse
# import io
# import os
# import sys
# import logging
# from abc import ABC, abstractmethod
# from dataclasses import dataclass

# class AudioDropoutCollapser:
#     _CHUNK_SIZE = 8192

#     def __init__(self, threshold: int, eps: float|None = None, detect_only: bool = False):
#         self._threshold = threshold
#         self._eps = eps
#         self._detect_only = detect_only

#     def collapse(self, input: RWaveReader, output: RWaveWriter|None):
#         zero_sample_predicate = None
#         if input.is_float():
#             zero_sample_predicate = FloatZeroSamplePredicate(input.get_sample_width(), self._eps)
#         else:
#             zero_sample_predicate = IntZeroSamplePredicate(input.get_sample_width(), self._eps)

#         num_frames = input.count_frames()
#         sample_rate = input.get_frame_rate()
#         total_length_in_seconds = self._format_num_samples_in_seconds(num_frames, sample_rate)
#         logging.debug(f'Length: {total_length_in_seconds} / Number of frames: {num_frames}')

#         pos = 0
#         num_prev_trailing_zeros = 0
#         while (pos < num_frames):
#             logging.trace(f'Position: frame {pos}')
#             chunk = input.read(self._CHUNK_SIZE)
#             num_prev_trailing_zeros = \
#                     self._collapse_chunk(output, chunk, sample_rate,
#                     num_prev_trailing_zeros, pos, zero_sample_predicate)
#             pos += len(chunk)
#         # assert pos == num_frames
#         if 0 < num_prev_trailing_zeros:
#             self._report_dropout(pos - num_prev_trailing_zeros, num_prev_trailing_zeros, sample_rate)

#     def _collapse_chunk(self, output: RWaveWriter,
#                 chunk: AudioFrameBuffer, sample_rate: int,
#                 num_prev_trailing_zeros: int, pos: int,
#                 zero_sample_predicate: ZeroSamplePredicate):
#         num_leading_zeros = chunk.count_leading_zeros(zero_sample_predicate)
#         logging.trace(f'Leading zeros: {num_leading_zeros}')
#         zero_run_length = num_prev_trailing_zeros + num_leading_zeros
#         if len(chunk) <= num_leading_zeros:
#             # all of the chunk is dropped
#             return zero_run_length
#         if zero_run_length >= self._threshold:
#             self._report_dropout(pos - num_prev_trailing_zeros, zero_run_length, sample_rate)

#         processed_bytes = num_leading_zeros
#         for zero_run_start, zero_run_length \
#                 in chunk.iterate_inner_zero_runs(zero_sample_predicate, self._threshold):
#             self._report_dropout(
#                 (pos + zero_run_start) if output is None else output.tell(),
#                 zero_run_length, sample_rate)
#             if output:
#                 sliced = chunk.slice(processed_bytes, zero_run_start)
#                 logging.trace(f'writing {len(sliced)} bytes data')
#                 output.write(sliced)
#             processed_bytes = zero_run_start + zero_run_length

#         num_trailing_zeros = chunk.count_trailing_zeros(zero_sample_predicate)
#         logging.trace(f'Trailing zeros: {num_trailing_zeros}')
#         if output:
#             sliced = chunk.slice(processed_bytes, len(chunk) - num_trailing_zeros)
#             logging.trace(f'writing {len(sliced)} bytes data')
#             output.write(sliced)
#         return num_trailing_zeros

#     def _report_dropout(self, abs_zero_run_start: int, zero_run_length: int, sample_rate: int):
#         s_abs_start = self._format_num_samples_in_seconds(abs_zero_run_start, sample_rate)
#         s_abs_end = self._format_num_samples_in_seconds(abs_zero_run_start + zero_run_length, sample_rate)
#         logging.info(_('cwd.zero_run_detected'),
#                 {'abs_start': s_abs_start, 'abs_end': s_abs_end, 'length': zero_run_length})
#         logging.debug(f'(at sample {abs_zero_run_start})')

#     def _format_num_samples_in_seconds(self, num_samples: int, sample_rate: int):
#         total_ms = num_samples * 1000 // sample_rate
#         minutes, ms = divmod(total_ms, 60_000)
#         seconds, ms = divmod(ms, 1000)
#         return f'{minutes:02}:{seconds:02}.{ms:03}'

# class AudioFrameBuffer:
#     def __init__(self, frames_as_bytes: bytes, sample_width: int):
#         self._frames_as_bytes = frames_as_bytes
#         self._sample_width = sample_width

#     def __len__(self):
#         '''
#         Returns the number of samples contained in this buffer
#         '''
#         return len(self._frames_as_bytes) // self._sample_width

#     def count_leading_zeros(self, predicate: ZeroSamplePredicate) -> int:
#         count = 0
#         for i in range(0, len(self._frames_as_bytes), self._sample_width):
#             if predicate.is_zero_sample(self._frames_as_bytes, i):
#                 count += 1
#             else:
#                 break
#         return count

#     def count_trailing_zeros(self, predicate: ZeroSamplePredicate) -> int:
#         count = 0
#         i = len(self._frames_as_bytes) - self._sample_width
#         while i >= 0 and predicate.is_zero_sample(self._frames_as_bytes, i):
#             count += 1
#             i -= self._sample_width
#         return count

#     def iterate_inner_zero_runs(self, predicate: ZeroSamplePredicate, threshold: int):
#         # skip leading and trailing zeros
#         i = self.count_leading_zeros(predicate) * self._sample_width

#         # scan inner dropouts
#         num_bytes = len(self._frames_as_bytes)
#         zero_run_length = 0
#         zero_run_start = None
#         while i < num_bytes:
#             if predicate.is_zero_sample(self._frames_as_bytes, i):
#                 if 0 == zero_run_length:
#                     zero_run_start = i // self._sample_width
#                 zero_run_length += 1
#             else:
#                 if zero_run_length > 0:
#                     if zero_run_length >= threshold:
#                         yield (zero_run_start, zero_run_length)
#                     zero_run_length = 0
#             i += self._sample_width

#     def slice(self, start: int, end: int):
#         return self._frames_as_bytes[start * self._sample_width:
#                 end * self._sample_width]

class StripZsndApp(TyperApp):
    def __init__(self, app_dir: Path):
        super().__init__('strip-zsnd', app_dir)

    def configure_i18n(self):
        super().configure_i18n()

        # FIXME 書式が違い危険なのでやめる
        # replace argparse’s gettext with i18nice
        # argparse._ = _

    def boot(self, args):
        super().boot(args)
        self.register_command(self._do_strip, 'strip')

    def _do_strip(self):
        pass

        # arg_parser = argparse.ArgumentParser(description=_('app.description'),
        #         formatter_class=argparse.RawDescriptionHelpFormatter)
        # arg_parser.add_argument('input', help=_('app.args.input'))
        # arg_parser.add_argument('output', help=_('app.args.output'),
        #         nargs='?')
        # arg_parser.add_argument('-t', '--threshold', help=_('app.args.threshold'),
        #         type=int, default=220)
        # arg_parser.add_argument('-e', '--eps', help=_('app.args.eps') % {
        #     'int_eps': IntZeroSamplePredicate.DEFAULT_EPS,
        #     'float_eps': FloatZeroSamplePredicate.DEFAULT_EPS,
        # }, type=float)
        # arg_parser.add_argument('--detect', help=_('app.args.detect'),
        #         action='store_true')
        # arg_parser.add_argument('-v', '--verbose', help=_('app.args.verbose'),
        #         action='count', default=0)
        # args = arg_parser.parse_args(sys.argv[1:])

#     def run(self) -> int:
#         arg_parser = argparse.ArgumentParser(description=_('app.description'),
#                 formatter_class=argparse.RawDescriptionHelpFormatter)
#         arg_parser.add_argument('input', help=_('app.args.input'))
#         arg_parser.add_argument('output', help=_('app.args.output'),
#                 nargs='?')
#         arg_parser.add_argument('-t', '--threshold', help=_('app.args.threshold'),
#                 type=int, default=220)
#         arg_parser.add_argument('-e', '--eps', help=_('app.args.eps',
#             int_eps=IntZeroSamplePredicate.DEFAULT_EPS,
#             float_eps=f'{FloatZeroSamplePredicate.DEFAULT_EPS:.2e}',
#         ), type=float)
#         arg_parser.add_argument('--detect', help=_('app.args.detect'),
#                 action='store_true')
#         arg_parser.add_argument('-v', '--verbose', help=_('app.args.verbose'),
#                 action='count', default=0)
#         args = arg_parser.parse_args(sys.argv[1:])

#         return self._do_run(args)

#     def _create_reader(self, path: str):
#         try:
#             f = io.open(path, 'rb')
#             try:
#                 # Wave_read does not close the file if it is created by an opend file
#                 return (f, RWaveReader(WaveFormatParser(), f))
#             except BaseException as exc:
#                 f.close()
#                 raise
#         except Exception as exc:
#             logging.error(_('cwd.input_file_cannot_be_opened'),
#                     {'f': path, 'exc': str(exc)})
#             logging.debug('', exc_info=True)
#             return (None, None)

#     def _create_writer(self, path: str, reader: RWaveReader):
#         try:
#             outf = io.open(path, 'wb')
#             try:
#                 return (outf, RWaveWriter(outf, reader))
#             except BaseException as exc:
#                 outf.close()
#                 raise
#         except Exception as exc:
#             logging.error(_('cwd.output_file_cannot_be_opened'),
#                     {'f': path, 'exc': str(exc)})
#             logging.debug('', exc_info=True)
#             return (None, None)

#     def _do_run(self, args: argparse.Namespace) -> int:
#         outf: io.BufferedWriter|None = None
#         output = None
#         f, input = self._create_reader(args.input)
#         if input is None:
#             return 1
#         try:
#             if not args.detect:
#                 output_p, ext = os.path.splitext(args.input)
#                 output_path = args.output or f'{output_p}-fix{ext}'
#                 outf, output = self._create_writer(output_path, input)
#                 if output is None:
#                     return 1

#             # output_file = "output.wav"
#             collapser = AudioDropoutCollapser(threshold=args.threshold, eps=args.eps,
#                     detect_only=args.detect)
#             collapser.collapse(input, output)
#             return 0
#         except Exception as exc:
#             logging.error(str(exc))
#             logging.debug('', exc_info=True)
#             return 1
#         finally:
#             output and output.close()
#             outf and outf.close()
#             input.close()
#             f.close()

# class ZeroSamplePredicate(ABC):
#     def __init__(self, sample_width_in_bytes: int):
#         self.sample_width_in_bytes = sample_width_in_bytes

#     @abstractmethod
#     def is_zero_sample(self, frames_as_bytes: bytes, pos: int):
#         pass

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

# class RWaveReader:
#     def __init__(self, waveFormatParser: WaveFormatParser, f: io.BufferedIOBase):
#         self._wave_format = waveFormatParser.parse(f)
#         logging.debug(self._wave_format)

#         f.seek(0)
#         self._wave_read: wave.Wave_read = wave.open(f)
#         logging.debug(self._wave_read.getparams())
#         if 2 <= self._wave_read.getnchannels():
#             self._wave_read.close()
#             raise RAudioException(_('r.error.mono_only_supported'))

#     def close(self):
#         self._wave_read.close()

#     def read(self, num_frames: int) -> AudioFrameBuffer:
#         width_in_bytes = self._wave_read.getsampwidth()
#         frames_as_bytes = self._wave_read.readframes(num_frames)
#         return AudioFrameBuffer(frames_as_bytes, width_in_bytes)

#     def is_float(self):
#         return self._wave_format.is_float()
    
#     def get_sample_width(self) -> int:
#         return self._wave_read.getsampwidth()

#     def get_frame_rate(self) -> int:
#         return self._wave_read.getframerate()

#     def count_frames(self) -> int:
#         """
#         Return the number of frames.
#         Each frame consists of one sample from every channel.
#         """
#         return self._wave_read.getnframes()

# class RWaveWriter:
#     def __init__(self, f: io.BufferedIOBase, reader: RWaveReader):
#         self._wave_write: wave.Wave_write = wave.open(f, 'wb')
#         self._wave_write.setnchannels(1)
#         self._wave_write.setsampwidth(reader.get_sample_width())
#         self._wave_write.setframerate(reader.get_frame_rate())

#     def write(self, data: bytes):
#         self._wave_write.writeframes(data)

#     def close(self):
#         self._wave_write.close()

#     def tell(self):
#         return self._wave_write.tell()

# @dataclass
# class WaveFormat:
#     """
#     See Also: https://learn.microsoft.com/ja-jp/windows/win32/api/mmeapi/ns-mmeapi-waveformatex
#     """
#     FORMAT_TAG_PCM          = 0x0001
#     FORMAT_TAG_FLOAT        = 0x0003
#     FORMAT_TAG_EXTENSIBLE   = 0xFFFE
#     KSDATAFORMAT_SUBTYPE_PCM = bytes.fromhex(
#             '01000000 0000 0010 8000 00AA00389B71'.replace(' ', ''))
#     KSDATAFORMAT_SUBTYPE_IEEE_FLOAT = bytes.fromhex(
#             '03000000 0000 0010 8000 00AA00389B71'.replace(' ', ''))

#     wFormatTag: int
#     nChannels: int
#     nSamplesPerSec: int
#     nAvgBytesPerSec: int
#     nBlockAlign: int
#     wBitsPerSample: int
#     wValidBitsPerSample: int|None
#     dwChannelMask: int|None
#     SubFormat: bytes|None # GUID

#     def is_pcm(self):
#         if self.wFormatTag == self.FORMAT_TAG_PCM:
#             return True
#         if self.wFormatTag == self.FORMAT_TAG_EXTENSIBLE:
#             return self.SubFormat == self.KSDATAFORMAT_SUBTYPE_PCM
#         return False
    
#     def is_float(self):
#         if self.wFormatTag == self.FORMAT_TAG_FLOAT:
#             return True
#         if self.wFormatTag == self.FORMAT_TAG_EXTENSIBLE:
#             return self.SubFormat == self.KSDATAFORMAT_SUBTYPE_IEEE_FLOAT
#         return False

# class WaveFormatParser:
#     def parse(self, f: io.BufferedIOBase):
#         if not hasattr(f, 'readable') or not f.readable():
#             raise RAudioException('passed stream is not readable')
#         try:
#             magic_riff, size, magic_wave = struct.unpack('<4sI4s', f.read(12))
#             if b'RIFF' != magic_riff or b'WAVE' != magic_wave:
#                 RAudioException(_('r.error.unsupported_format_exc') % 'magic bytes not found')
#             while True:
#                 header = f.read(8)
#                 if len(header) < 8:
#                         RAudioException(_('r.error.unsupported_format_exc') % 'fmt chunk not found')
#                 chunk_id, chunk_size = struct.unpack('<4sI', header)
#                 if chunk_id == b'fmt ':
#                     fmt_chunk = f.read(chunk_size)
#                     return self._parse_fmt_chunk(fmt_chunk)
#                 else:
#                     f.seek(chunk_size, 1)
#         except RAudioException as exc:
#             raise
#         except Exception as exc:
#             raise RAudioException(_('r.error.unsupported_format_exc') % str(exc)) from exc

#     def _parse_fmt_chunk(self, fmt_chunk: bytes):
#         wFormatTag, nChannels, nSamplesPerSec, nAvgBytesPerSec, \
#         nBlockAlign, wBitsPerSample = struct.unpack('<HHIIHH', fmt_chunk[:16])
#         wValidBitsPerSample = dwChannelMask = SubFormat = None
#         if WaveFormat.FORMAT_TAG_EXTENSIBLE == wFormatTag:
#             wValidBitsPerSample, dwChannelMask, SubFormat = \
#                     struct.unpack('<HI16s', fmt_chunk[18:40])
#         return WaveFormat(wFormatTag, nChannels, nSamplesPerSec, nAvgBytesPerSec, \
#                 nBlockAlign, wBitsPerSample,
#                 wValidBitsPerSample, dwChannelMask, SubFormat)

# class RAudioException(Exception):
#     pass
