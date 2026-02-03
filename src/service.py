from wav_io import ZsndWavReader, ZsndWavWriter
from util import LogMixin

# from i18n import t as _

from abc import ABC, abstractmethod

class StrippingEventListener(ABC):
    @abstractmethod
    def on_update_progress(self, num_processed_frames, num_total_frames):
        pass

class StripZsndService(LogMixin):
    _CHUNK_SIZE = 8192

    def __init__(self, listener: StrippingEventListener|None):
        self.listener = listener

    def strip(self, reader: ZsndWavReader, writer: ZsndWavWriter|None, min_duration: int, threshold: float, detect_only: bool = False):
#         self._threshold = threshold
#         self._eps = eps
#         self._detect_only = detect_only

#         zero_sample_predicate = None
#         if input.is_float():
#             zero_sample_predicate = FloatZeroSamplePredicate(input.get_sample_width(), self._eps)
#         else:
#             zero_sample_predicate = IntZeroSamplePredicate(input.get_sample_width(), self._eps)

        num_frames = reader.count_frames()
#         sample_rate = input.get_frame_rate()
#         total_length_in_seconds = self._format_num_samples_in_seconds(num_frames, sample_rate)
#         logging.debug(f'Length: {total_length_in_seconds} / Number of frames: {num_frames}')


        from time import sleep
        pos = 0
#         num_prev_trailing_zeros = 0
        while (pos < num_frames):
#             logging.trace(f'Position: frame {pos}')
            chunk = reader.read(self._CHUNK_SIZE)
            if 0 >= len(chunk):  # EOF
                break
#             num_prev_trailing_zeros = \
#                     self._collapse_chunk(output, chunk, sample_rate,
#                     num_prev_trailing_zeros, pos, zero_sample_predicate)
            pos += len(chunk)
            self.listener and self.listener.on_update_progress(pos, num_frames)
        if pos != num_frames:
            self.get_logger().warning(
                    f'Processed data length "{pos}" does not match the length calculated at the start "{num_frames}]"')
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
