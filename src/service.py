from wav_logic import WavZeroSoundPredicateFactory
from wav_io import ZsndWavChunk, ZsndWavReader, ZsndWavWriter, ZeroSoundPredicate
from util import LogMixin

from i18n import t as _
from typing import Iterable

class StripZsndService(LogMixin):
    _CHUNK_SIZE = 8192

    def strip(self, reader: ZsndWavReader, writer: ZsndWavWriter|None,
                min_duration_in_ms: int, threshold: float, detect_only: bool = False) \
            -> Iterable[tuple[int, int]]:
        '''
        :rtype: Iterable[tuple[int, int]] yield (postion, total)
        '''
        logger = self.get_logger()

        num_frames = reader.count_frames()
        sample_rate = reader.get_sample_rate()
        total_length_in_seconds = self._format_num_samples_in_seconds(num_frames, sample_rate)
        logger.debug(f'Length: {total_length_in_seconds} / Number of frames: {num_frames}')

        min_duration_in_samples = (sample_rate * min_duration_in_ms) // 1000

        zero_sound_predicate = WavZeroSoundPredicateFactory().create(reader, threshold)

        pos = 0
        num_prev_trailing_zeros = 0
        while (pos < num_frames):
            logger.trace(f'Position: frame {pos}')
            chunk = reader.read(self._CHUNK_SIZE)
            if 0 >= len(chunk):  # EOF
                break

            num_prev_trailing_zeros = self._collapse_chunk(chunk, num_prev_trailing_zeros, pos,
                    zero_sound_predicate, writer, sample_rate, min_duration_in_samples)

            pos += len(chunk)
            yield reader.tell(), reader.count_frames()
        if pos != num_frames:
            self.get_logger().warning(
                    f'Processed data length "{pos}" does not match the length calculated at the start "{num_frames}]"')
        if num_prev_trailing_zeros >= min_duration_in_samples:
            self._report_dropout(pos - num_prev_trailing_zeros, num_prev_trailing_zeros, sample_rate)

    def _collapse_chunk(self, chunk: ZsndWavChunk, num_prev_trailing_zeros: int, pos: int,
                zero_sound_predicate: ZeroSoundPredicate, writer: ZsndWavWriter,
                sample_rate: int, min_duration_in_samples: int):
        logger = self.get_logger()

        num_leading_zeros = chunk.count_leading_zeros(zero_sound_predicate)
        logger.trace(f'Leading zeros: {num_leading_zeros}')
        zero_run_length = num_prev_trailing_zeros + num_leading_zeros
        if len(chunk) <= num_leading_zeros:
            # all of the chunk is dropped
            return zero_run_length
        if zero_run_length >= min_duration_in_samples:
            self._report_dropout(pos - num_prev_trailing_zeros, zero_run_length, sample_rate)

        processed_bytes = num_leading_zeros
        for zero_run_start, zero_run_length \
                in chunk.iterate_inner_zero_runs(zero_sound_predicate):
            if zero_run_length < min_duration_in_samples:
                continue
            self._report_dropout(
                (pos + zero_run_start) if writer is None else writer.tell(),
                zero_run_length, sample_rate)
#             if output:
#                 sliced = chunk.slice(processed_bytes, zero_run_start)
#                 logging.trace(f'writing {len(sliced)} bytes data')
#                 output.write(sliced)
            processed_bytes = zero_run_start + zero_run_length

        num_trailing_zeros = chunk.count_trailing_zeros(zero_sound_predicate)
        logger.trace(f'Trailing zeros: {num_trailing_zeros}')
#         if output:
#             sliced = chunk.slice(processed_bytes, len(chunk) - num_trailing_zeros)
#             logging.trace(f'writing {len(sliced)} bytes data')
#             output.write(sliced)
        return num_trailing_zeros

    def _report_dropout(self, abs_zero_run_start: int, zero_run_length: int, frame_rate: int):
        logger = self.get_logger()
        s_abs_start = self._format_num_samples_in_seconds(abs_zero_run_start, frame_rate)
        s_abs_end = self._format_num_samples_in_seconds(abs_zero_run_start + zero_run_length, frame_rate)
        logger.info(_('zsnd.zero_sound_detected') %
                {'abs_start': s_abs_start, 'abs_end': s_abs_end, 'length': zero_run_length})
        logger.debug(f'(at sample {abs_zero_run_start})')

    def _format_num_samples_in_seconds(self, num_samples: int, frame_rate: int):
        total_ms = num_samples * 1000 // frame_rate
        minutes, ms = divmod(total_ms, 60_000)
        seconds, ms = divmod(ms, 1000)
        return f'{minutes:02}:{seconds:02}.{ms:03}'
