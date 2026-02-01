# coding: utf-8
from __future__ import annotations

import wave
import struct
import argparse
import locale
import ctypes
import io
import os
import sys
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

MESSAGES = {
    'en': {
        'app.description': """A script to remove missing zero-samples from a WAV file

Removes zero-runs caused by buffer underflow during recording.
Waveforms that have cliffs in the middle cannot be repaired.""",
        'app.args.input': 'path to the input file',
        'app.args.output': 'path to the output file. default: [input]-fixed',
        'app.args.threshold': """minimum zero-run length to remove (samples). at 44kHz, 44 = 1ms. default: %(default)s""",
        'app.args.detect': 'detects zero-runs without creating any output file',
        'app.args.verbose': 'increases logging verbosity (e.g., -v, -vv, -vvv).',
        'app.args.eps': 'zero epsilon. default: int:%(int_eps)d, float:%(float_eps).2e',

        'r.error.unsupported_format': 'Unsupported format',
        'r.error.unsupported_format_exc': 'Unsupported format: %s',
        'r.error.mono_only_supported': 'Supports mono audio sources only',

        'cwd.input_file_cannot_be_opened': 'Input file "%(f)s" cannot be opened:\n%(exc)s',
        'cwd.zero_run_detected': '%(abs_start)s-%(abs_end)s (%(length)d samples) lacked',
    },
    'es': {
        'app.description': """Un script para eliminar las muestras cero que faltan en un archivo WAV

Elimina las pérdidas de datos por cero causadas por problemas de grabación, como el desbordamiento del búfer.
Las formas de onda que presentan saltos en el medio no se pueden reparar.""",
        'app.args.input': 'ruta al archivo de entrada',
        'app.args.output': 'ruta al archivo de salida. predeterminado: [input]-fixed',
        'app.args.threshold': """longitud mínima de ejecución cero para eliminar (muestras). at 44kHz, 44 = 1ms. predeterminado: %(default)s""",
        'app.args.detect': 'detecta secuencias de ceros sin crear ningún archivo de salida',
        'app.args.verbose': 'aumentar la verbosidad del registro (por ejemplo, -v, -vv, -vvv)',
        'app.args.eps': 'épsilon. predeterminado: int:%(int_eps)d, float:%(float_eps).2e',

        'argparse.usage: ': 'uso: ',
        'argparse.positional arguments': 'argumentos posicionales',
        'argparse.options': 'opciones',
        'argparse.show this help message and exit': 'mostrar este mensaje de ayuda y salir',

        'r.error.unsupported_format': 'Formato no compatible',
        'r.error.unsupported_format_exc': 'Formato no compatible: %s',
        'r.error.mono_only_supported': 'Solo admite fuentes de audio mono',

        'cwd.input_file_cannot_be_opened': 'No se puede abrir el archivo de entrada "%(f)s"\n%(exc)s',
        'cwd.zero_run_detected': '%(abs_start)s-%(abs_end)s (%(length)d muestras) carecían de',
    },
    'ja': {
        'app.description': """WAVファイルの欠落0サンプルを除去するスクリプト

録音時のバッファアンダーフローなどで発生する、連続した0サンプルを取り除きます.
0サンプルではなく、波形が途中で飛んで断崖になっているものは直りません.

直る(可能性のある)波形\t／|＿|＼

直らない波形\t\t＿＿|￣￣""",
        'app.args.input': '入力ファイルのパス',
        'app.args.output': '出力ファイルのパス. デフォルト: [input]-fixed',
        'app.args.threshold': 'ドロップアウトとみなす最小長. 単位はサンプル数. 44kHzで44なら1ms. デフォルト: %(default)s',
        'app.args.eps': 'ゼロとみなす最大値. デフォルト: int:%(int_eps)d, float:%(float_eps).2e',
        'app.args.verbose': 'ログメッセージの詳細度. -vvvで最大',

        'app.args.detect': '検出のみを行い、出力しません',
        'argparse.usage: ': '使い方: ',
        'argparse.positional arguments': '位置引数',
        'argparse.options': 'オプション引数',
        'argparse.show this help message and exit': 'このメッセージを表示して終了します',
        'argparse.the following arguments are required: input': '入力ファイルのパスを入力してください',

        'r.error.unsupported_format': 'サポートされていないフォーマット',
        'r.error.unsupported_format_exc': 'サポートされていないフォーマット: %s',
        'r.error.mono_only_supported': 'モノラル音源のみのサポートです',

        'cwd.input_file_cannot_be_opened': '入力ファイル "%(f)s" を開けません:\n%(exc)s',
        'cwd.zero_run_detected': '%(abs_start)s-%(abs_end)s (%(length)dサンプル) 欠落',
    },
}

LOG_LEVEL_TRACE = 5

class AudioDropoutCollapser:
    _CHUNK_SIZE = 8192

    def __init__(self, threshold: int, eps: float|None = None, detect_only: bool = False):
        self._threshold = threshold
        self._eps = eps
        self._detect_only = detect_only

    def collapse(self, input: RWaveReader, output: RWaveWriter|None):
        zero_sample_predicate = None
        if input.is_float():
            zero_sample_predicate = FloatZeroSamplePredicate(input.get_sample_width(), self._eps)
        else:
            zero_sample_predicate = IntZeroSamplePredicate(input.get_sample_width(), self._eps)

        num_frames = input.count_frames()
        sample_rate = input.get_frame_rate()
        total_length_in_seconds = self._format_num_samples_in_seconds(num_frames, sample_rate)
        logging.debug(f'Length: {total_length_in_seconds} / Number of frames: {num_frames}')

        pos = 0
        num_prev_trailing_zeros = 0
        while (pos < num_frames):
            logging.trace(f'Position: frame {pos}')
            chunk = input.read(self._CHUNK_SIZE)
            num_prev_trailing_zeros = \
                    self._collapse_chunk(output, chunk, sample_rate,
                    num_prev_trailing_zeros, pos, zero_sample_predicate)
            pos += len(chunk)
        # assert pos == num_frames
        if 0 < num_prev_trailing_zeros:
            self._report_dropout(pos - num_prev_trailing_zeros, num_prev_trailing_zeros, sample_rate)

    def _collapse_chunk(self, output: RWaveWriter,
                chunk: AudioFrameBuffer, sample_rate: int,
                num_prev_trailing_zeros: int, pos: int,
                zero_sample_predicate: ZeroSamplePredicate):
        num_leading_zeros = chunk.count_leading_zeros(zero_sample_predicate)
        logging.trace(f'Leading zeros: {num_leading_zeros}')
        zero_run_length = num_prev_trailing_zeros + num_leading_zeros
        if len(chunk) <= num_leading_zeros:
            # all of the chunk is dropped
            return zero_run_length
        if zero_run_length >= self._threshold:
            self._report_dropout(pos - num_prev_trailing_zeros, zero_run_length, sample_rate)

        processed_bytes = num_leading_zeros
        for zero_run_start, zero_run_length \
                in chunk.iterate_inner_zero_runs(zero_sample_predicate, self._threshold):
            self._report_dropout(
                (pos + zero_run_start) if output is None else output.tell(),
                zero_run_length, sample_rate)
            if output:
                sliced = chunk.slice(processed_bytes, zero_run_start)
                logging.trace(f'writing {len(sliced)} bytes data')
                output.write(sliced)
            processed_bytes = zero_run_start + zero_run_length

        num_trailing_zeros = chunk.count_trailing_zeros(zero_sample_predicate)
        logging.trace(f'Trailing zeros: {num_trailing_zeros}')
        if output:
            sliced = chunk.slice(processed_bytes, len(chunk) - num_trailing_zeros)
            logging.trace(f'writing {len(sliced)} bytes data')
            output.write(sliced)
        return num_trailing_zeros

    def _report_dropout(self, abs_zero_run_start: int, zero_run_length: int, sample_rate: int):
        s_abs_start = self._format_num_samples_in_seconds(abs_zero_run_start, sample_rate)
        s_abs_end = self._format_num_samples_in_seconds(abs_zero_run_start + zero_run_length, sample_rate)
        logging.info(_('cwd.zero_run_detected'),
                {'abs_start': s_abs_start, 'abs_end': s_abs_end, 'length': zero_run_length})
        logging.debug(f'(at sample {abs_zero_run_start})')

    def _format_num_samples_in_seconds(self, num_samples: int, sample_rate: int):
        total_ms = num_samples * 1000 // sample_rate
        minutes, ms = divmod(total_ms, 60_000)
        seconds, ms = divmod(ms, 1000)
        return f'{minutes:02}:{seconds:02}.{ms:03}'

class AudioFrameBuffer:
    def __init__(self, frames_as_bytes: bytes, sample_width: int):
        self._frames_as_bytes = frames_as_bytes
        self._sample_width = sample_width

    def __len__(self):
        '''
        Returns the number of samples contained in this buffer
        '''
        return len(self._frames_as_bytes) // self._sample_width

    def count_leading_zeros(self, predicate: ZeroSamplePredicate) -> int:
        count = 0
        for i in range(0, len(self._frames_as_bytes), self._sample_width):
            if predicate.is_zero_sample(self._frames_as_bytes, i):
                count += 1
            else:
                break
        return count

    def count_trailing_zeros(self, predicate: ZeroSamplePredicate) -> int:
        count = 0
        i = len(self._frames_as_bytes) - self._sample_width
        while i >= 0 and predicate.is_zero_sample(self._frames_as_bytes, i):
            count += 1
            i -= self._sample_width
        return count

    def iterate_inner_zero_runs(self, predicate: ZeroSamplePredicate, threshold: int):
        # skip leading and trailing zeros
        i = self.count_leading_zeros(predicate) * self._sample_width

        # scan inner dropouts
        num_bytes = len(self._frames_as_bytes)
        zero_run_length = 0
        zero_run_start = None
        while i < num_bytes:
            if predicate.is_zero_sample(self._frames_as_bytes, i):
                if 0 == zero_run_length:
                    zero_run_start = i // self._sample_width
                zero_run_length += 1
            else:
                if zero_run_length > 0:
                    if zero_run_length >= threshold:
                        yield (zero_run_start, zero_run_length)
                    zero_run_length = 0
            i += self._sample_width

    def slice(self, start: int, end: int):
        return self._frames_as_bytes[start * self._sample_width:
                end * self._sample_width]

class AudioDropoutCollapserApp:
    def run(self) -> int:
        log_configurator = LogConfigurator()
        log_configurator.configre()

        # reflect OS locale
        locale.setlocale(locale.LC_ALL)

        i18n = RI18n(MESSAGES, 'en')
        i18n.set_as_app_default()
        R18nGettextHook(i18n, argparse, '_', 'argparse.').hook()

        arg_parser = argparse.ArgumentParser(description=_('app.description'),
                formatter_class=argparse.RawDescriptionHelpFormatter)
        arg_parser.add_argument('input', help=_('app.args.input'))
        arg_parser.add_argument('output', help=_('app.args.output'),
                nargs='?')
        arg_parser.add_argument('-t', '--threshold', help=_('app.args.threshold'),
                type=int, default=220)
        arg_parser.add_argument('-e', '--eps', help=_('app.args.eps') % {
            'int_eps': IntZeroSamplePredicate.DEFAULT_EPS,
            'float_eps': FloatZeroSamplePredicate.DEFAULT_EPS,
        }, type=float)
        arg_parser.add_argument('--detect', help=_('app.args.detect'),
                action='store_true')
        arg_parser.add_argument('-v', '--verbose', help=_('app.args.verbose'),
                action='count', default=0)
        args = arg_parser.parse_args(sys.argv[1:])

        log_configurator.configre(args.verbose)

        return self._do_run(args)

    def _create_reader(self, path: str):
        try:
            f = io.open(path, 'rb')
            try:
                # Wave_read does not close the file if it is created by an opend file
                return (f, RWaveReader(WaveFormatParser(), f))
            except BaseException as exc:
                f.close()
                raise
        except Exception as exc:
            logging.error(_('cwd.input_file_cannot_be_opened'),
                    {'f': path, 'exc': str(exc)})
            logging.debug('', exc_info=True)
            return (None, None)

    def _create_writer(self, path: str, reader: RWaveReader):
        try:
            outf = io.open(path, 'wb')
            try:
                return (outf, RWaveWriter(outf, reader))
            except BaseException as exc:
                outf.close()
                raise
        except Exception as exc:
            logging.error(_('cwd.output_file_cannot_be_opened'),
                    {'f': path, 'exc': str(exc)})
            logging.debug('', exc_info=True)
            return (None, None)

    def _do_run(self, args: argparse.Namespace) -> int:
        outf: io.BufferedWriter|None = None
        output = None
        f, input = self._create_reader(args.input)
        if input is None:
            return 1
        try:
            if not args.detect:
                output_p, ext = os.path.splitext(args.input)
                output_path = args.output or f'{output_p}-fix{ext}'
                outf, output = self._create_writer(output_path, input)
                if output is None:
                    return 1

            # output_file = "output.wav"
            collapser = AudioDropoutCollapser(threshold=args.threshold, eps=args.eps,
                    detect_only=args.detect)
            collapser.collapse(input, output)
            return 0
        except Exception as exc:
            logging.error(str(exc))
            logging.debug('', exc_info=True)
            return 1
        finally:
            output and output.close()
            outf and outf.close()
            input.close()
            f.close()

class ZeroSamplePredicate(ABC):
    def __init__(self, sample_width_in_bytes: int):
        self.sample_width_in_bytes = sample_width_in_bytes

    @abstractmethod
    def is_zero_sample(self, frames_as_bytes: bytes, pos: int):
        pass

class IntZeroSamplePredicate(ZeroSamplePredicate):
    DEFAULT_EPS = 1

    def __init__(self, sample_width_in_bytes: int, eps: int = DEFAULT_EPS):
        super().__init__(sample_width_in_bytes)
        if eps is None:
            self._eps = self.DEFAULT_EPS
        else:
            self._eps = int(eps)

    def is_zero_sample(self, frames_as_bytes, pos):
        # positive integer
        if self._eps >= frames_as_bytes[pos]:
            for i in range(1, self.sample_width_in_bytes):
                if 0 != frames_as_bytes[pos+i]:
                    return False
            return True
        # negative integer
        if self._eps >= (0x100 - frames_as_bytes[pos]):
            for i in range(1, self.sample_width_in_bytes):
                if 0xFF != frames_as_bytes[pos+i]:
                    return False
            return True
        return False

class FloatZeroSamplePredicate(ZeroSamplePredicate):
    DEFAULT_EPS = 1e-9

    def __init__(self, sample_width_in_bytes: int, eps: float = DEFAULT_EPS):
        super().__init__(sample_width_in_bytes)
        if eps is None:
            self._eps = self.DEFAULT_EPS
        else:
            self._eps = eps
        match sample_width_in_bytes:
            case 4:
                self._unpacker = struct.Struct('<f')
            case 8:
                self._unpacker = struct.Struct('<d')
            case _:
                raise RAudioException('Unsupported float format')

    def is_zero_sample(self, frames_as_bytes, pos):
        sliced = frames_as_bytes[pos:(pos+self.sample_width_in_bytes)]
        fp = self._unpacker.unpack(sliced)[0]
        return self._eps >= abs(fp)

class RWaveReader:
    def __init__(self, waveFormatParser: WaveFormatParser, f: io.BufferedIOBase):
        self._wave_format = waveFormatParser.parse(f)
        logging.debug(self._wave_format)

        f.seek(0)
        self._wave_read: wave.Wave_read = wave.open(f)
        logging.debug(self._wave_read.getparams())
        if 2 <= self._wave_read.getnchannels():
            self._wave_read.close()
            raise RAudioException(_('r.error.mono_only_supported'))

    def close(self):
        self._wave_read.close()

    def read(self, num_frames: int) -> AudioFrameBuffer:
        width_in_bytes = self._wave_read.getsampwidth()
        frames_as_bytes = self._wave_read.readframes(num_frames)
        return AudioFrameBuffer(frames_as_bytes, width_in_bytes)

    def is_float(self):
        return self._wave_format.is_float()
    
    def get_sample_width(self) -> int:
        return self._wave_read.getsampwidth()

    def get_frame_rate(self) -> int:
        return self._wave_read.getframerate()

    def count_frames(self) -> int:
        """
        Return the number of frames.
        Each frame consists of one sample from every channel.
        """
        return self._wave_read.getnframes()

class RWaveWriter:
    def __init__(self, f: io.BufferedIOBase, reader: RWaveReader):
        self._wave_write: wave.Wave_write = wave.open(f, 'wb')
        self._wave_write.setnchannels(1)
        self._wave_write.setsampwidth(reader.get_sample_width())
        self._wave_write.setframerate(reader.get_frame_rate())

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

class RI18n:
    def __init__(self,
            message_dict: dict[str, dict[str, str]],
            fallback_lang: str,
            locale_id:str|None = None):
        """
        :param locale_id: If None, defaults to locale.getlocale()[0].
        """
        if locale_id is None:
            locale_id = locale.getlocale()[0]

        self._message_dict = message_dict
        self._fallback_dict_for_lang = self._message_dict[fallback_lang]

        lang = self._resolve_lang_for_init(locale_id)
        if lang is None:
            self._dict_for_lang = self._fallback_dict_for_lang
        else:
            self._dict_for_lang = self._message_dict[lang]

    def _resolve_lang_for_init(self, locale_id: str) -> str | None:
        """
        Returns the closest supported language code for the given locale ID during initialization.

        :return: The resolved language code, or None if a fallback language should be used.
        """
        if locale_id:
            lang = locale_id.split('_')[0]
            if (lang in self._message_dict):
                return lang
        # On Windows, the locale ID may not be in POIX format
        if 'nt' == os.name:
            lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
            if lcid in locale.windows_locale:
                actual_locale_id = locale.windows_locale[lcid]
                lang = actual_locale_id.split('_')[0]
                if lang in self._message_dict:
                    return lang

    def get(self, key: str) -> str:
        return self.get_or_none(key) or key

    def get_or_none(self, key: str) -> str|None:
        msg = self._dict_for_lang.get(key,
                self._fallback_dict_for_lang.get(key))
        logger = logging.getLogger(__name__)
        if logger.isEnabledFor(LOG_LEVEL_TRACE):
            logger.trace('i18n:%s -> %s', key, msg)
        return msg

    def set_as_app_default(self):
        global _
        _ = lambda key: self.get(key)

class R18nGettextHook:
    def __init__(self, rI18n: RI18n, module: object, imported_name: str,
            key_prefix: str):
        self._rI18n = rI18n
        self._module = module
        self._imported_name = imported_name
        self._key_prefix = key_prefix
        self._orig_gettext = getattr(self._module, self._imported_name)

    def hook(self):
        proc = lambda key: self._rI18n.get_or_none(self._key_prefix + key) \
                or self._orig_gettext(key)
        setattr(self._module, self._imported_name, proc)

    def unhook(self):
        setattr(self._module, self._imported_name, self._orig_gettext)

class LogConfigurator:
    def configre(self, verbosity: int = 0):
        # remove existing handlers to reconfigure
        for h in logging.root.handlers:
            logging.root.removeHandler(h)

        if 'TRACE' not in logging._nameToLevel:
            logging.addLevelName(LOG_LEVEL_TRACE, 'TRACE')
            logging.Logger.trace = self.__class__._trace_impl
            logging.trace = self.__class__._root_trace_impl

        level = logging.INFO
        if 1 <= verbosity:
            level = logging.DEBUG
        if 3 <= verbosity:
            level = LOG_LEVEL_TRACE

        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    def _trace_impl(self: logging.Logger, msg, *args, **kwargs):
        """
        Implementation of logging.Logger.trace()
        """
        if self.isEnabledFor(LOG_LEVEL_TRACE):
            self._log(LOG_LEVEL_TRACE, msg, args, **kwargs)

    def _root_trace_impl(msg, *args, **kwargs):
        """
        Implementation of logging.trace()
        """
        logging.root.trace(msg, *args, **kwargs)

class RAudioException(Exception):
    pass

_: Callable[[str], str]
the_app = AudioDropoutCollapserApp()

if __name__ == '__main__':
    sys.exit(the_app.run())
