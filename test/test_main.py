from wav_io import ZsndWavReader, WavChunk
from wav_logic import _PcmIntZeroSoundPredicate
from wave_format import WaveFormat

import wave
import io
# from unittest.mock import patch
import unittest

# class TestAudioDropoutCollapser(unittest.TestCase):
#     def test_format_num_samples_in_ms(self):
#         collapser = cwd.AudioDropoutCollapser(441)
#         self.assertEqual('00:00.100',
#                 collapser._format_num_samples_in_seconds(4410, 44100))

#     def test_format_num_samples_in_seconds(self):
#         collapser = cwd.AudioDropoutCollapser(441)
#         self.assertEqual('00:01.000',
#                 collapser._format_num_samples_in_seconds(48000, 48000))

#     def test_format_num_samples_in_minutes(self):
#         collapser = cwd.AudioDropoutCollapser(441)
#         self.assertEqual('01:00.000',
#                 collapser._format_num_samples_in_seconds(2400_000, 40000))

#     def test_collapse_inner_zero_runs(self):
#         mid_point = 2 * cwd.AudioDropoutCollapser._CHUNK_SIZE
#         start = mid_point - 2 * 777
#         buf = io.BytesIO()
#         with wave.open(buf, 'wb') as w:
#             w.setnchannels(1)
#             w.setsampwidth(2)
#             w.setframerate(44100)
#             barr = bytearray([0x40] * (2 * mid_point))
#             barr[start:(start + 2*1000)] = bytes(2*1000)
#             w.writeframes(barr)
#         buf.seek(0)
#         reader = cwd.RWaveReader(cwd.WaveFormatParser(), buf)

#         collapser = cwd.AudioDropoutCollapser(441)
#         with patch.object(collapser, '_report_dropout') as mock_handler:
#             collapser.collapse(reader, None)
#         mock_handler.assert_called_once_with(start//2, 1000, 44100)

class TestWavChunk(unittest.TestCase):
    def _create_wave_foramt(self):
        # int16
        return WaveFormat(
            wFormatTag=WaveFormat.FORMAT_TAG_PCM,
            nChannels=1,
            nSamplesPerSec=44100,
            nAvgBytesPerSec=88200,
            nBlockAlign=2,
            wBitsPerSample=16,
        )

    def test_count_leading_zeros(self):
        predicate = _PcmIntZeroSoundPredicate(2, -80)
        bbuf = bytearray([0x40] * 4000)
        bbuf[:(2 * 200)] = bytes(2 * 200)
        chunk = WavChunk(bbuf, self._create_wave_foramt())
        self.assertEqual(200, chunk.count_leading_zeros(predicate))

    def test_count_trailing_zeros(self):
        predicate = _PcmIntZeroSoundPredicate(2, -80)
        bbuf = bytearray([0x40] * 4000)
        bbuf[-(2 * 200):] = bytes(2 * 200)
        chunk = WavChunk(bbuf, self._create_wave_foramt())
        self.assertEqual(200, chunk.count_trailing_zeros(predicate))

    def test_iterate_inner_zero_runs(self):
        predicate = _PcmIntZeroSoundPredicate(2, -80)
        bbuf = bytearray([0x40] * 4000)
        bbuf[(2 * 100):(2 * 200)] = bytes(2 * (200-100))
        bbuf[(2  *594):(2 * 680)] = bytes(2 * (680-594))
        chunk = WavChunk(bbuf, self._create_wave_foramt())
        self.assertEqual(list(chunk.iterate_inner_zero_runs(predicate, 22)),[
            (100, 200-100),
            (594, 680-594),
        ])

class TestZsndWavReader(unittest.TestCase):
    def test_read(self):
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            w.writeframes(bytes(2 * 40000))
        buf.seek(0)
        reader = ZsndWavReader(buf)
        num_samples = reader.count_frames()
        self.assertEqual(40000, num_samples)
        pos = 0
        while (pos < num_samples):
            b = reader.read(777)
            pos += len(b)
        self.assertEqual(pos, 40000)
