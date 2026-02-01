# coding: utf-8

from unittest.mock import patch
import unittest
import collapse_wav_dropouts as cwd
import wave
import numpy as np
import io
import random

class TestAudioDropoutCollapser(unittest.TestCase):
    def test_format_num_samples_in_ms(self):
        collapser = cwd.AudioDropoutCollapser(441)
        self.assertEqual('00:00.100',
                collapser._format_num_samples_in_seconds(4410, 44100))

    def test_format_num_samples_in_seconds(self):
        collapser = cwd.AudioDropoutCollapser(441)
        self.assertEqual('00:01.000',
                collapser._format_num_samples_in_seconds(48000, 48000))

    def test_format_num_samples_in_minutes(self):
        collapser = cwd.AudioDropoutCollapser(441)
        self.assertEqual('01:00.000',
                collapser._format_num_samples_in_seconds(2400_000, 40000))

    def test_collapse_inner_zero_runs(self):
        mid_point = 2 * cwd.AudioDropoutCollapser._CHUNK_SIZE
        start = mid_point - 2 * 777
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            barr = bytearray([0x40] * (2 * mid_point))
            barr[start:(start + 2*1000)] = bytes(2*1000)
            w.writeframes(barr)
        buf.seek(0)
        reader = cwd.RWaveReader(cwd.WaveFormatParser(), buf)

        collapser = cwd.AudioDropoutCollapser(441)
        with patch.object(collapser, '_report_dropout') as mock_handler:
            collapser.collapse(reader)
        mock_handler.assert_called_once_with(start//2, 1000, 44100)

class TestAudioFrameBuffer(unittest.TestCase):
    def test_count_leading_zeros(self):
        predicate = cwd.IntZeroSamplePredicate(2)
        bbuf = bytearray([0x40] * 4000)
        bbuf[:(2 * 200)] = bytes(2 * 200)
        audio_buffer = cwd.AudioFrameBuffer(bbuf, 2)
        self.assertEqual(200, audio_buffer.count_leading_zeros(predicate))

    def test_count_trailing_zeros(self):
        predicate = cwd.IntZeroSamplePredicate(2)
        bbuf = bytearray([0x40] * 4000)
        bbuf[-(2 * 200):] = bytes(2 * 200)
        audio_buffer = cwd.AudioFrameBuffer(bbuf, 2)
        self.assertEqual(200, audio_buffer.count_trailing_zeros(predicate))

    def test_iterate_inner_zero_runs(self):
        predicate = cwd.IntZeroSamplePredicate(2)
        bbuf = bytearray([0x40] * 4000)
        bbuf[(2 * 100):(2 * 200)] = bytes(2 * (200-100))
        bbuf[(2  *594):(2 * 680)] = bytes(2 * (680-594))
        audio_buffer = cwd.AudioFrameBuffer(bbuf, 2)
        self.assertEqual(list(audio_buffer.iterate_inner_zero_runs(predicate, 22)),[
            (100, 200-100),
            (594, 680-594),
        ])

class TestIntZeroSamplePredicate(unittest.TestCase):
    def test_positive_zero_samples_int16(self):
        self._do_test_positive_zero_samples_int(2)

    def test_positive_zero_samples_int24(self):
        self._do_test_positive_zero_samples_int(3)

    def test_positive_zero_samples_int32(self):
        self._do_test_positive_zero_samples_int(4)

    def _do_test_positive_zero_samples_int(self, width: int):
        count = 4000
        buf = bytearray(count * width)
        for i in range(0, count):
            buf[i * width] = random.randint(0,
                    cwd.IntZeroSamplePredicate.DEFAULT_EPS)
        predicate = cwd.IntZeroSamplePredicate(width)
        for i in range(0, len(buf) // width, width):
            self.assertTrue(predicate.is_zero_sample(buf, i), f'{i}: {buf[i:i+width]}')

    def test_negative_zero_samples_int16(self):
        self._do_test_negative_zero_samples_int(2)

    def test_negative_zero_samples_int24(self):
        self._do_test_negative_zero_samples_int(3)

    def test_negative_zero_samples_int32(self):
        self._do_test_negative_zero_samples_int(4)

    def _do_test_negative_zero_samples_int(self, width: int):
        count = 4000
        buf = bytearray([0xFF] * (count * width))
        for i in range(0, count):
            buf[i * width] = random.randint(
                    0xFF - cwd.IntZeroSamplePredicate.DEFAULT_EPS + 1, 0xFF)
        predicate = cwd.IntZeroSamplePredicate(width)
        for i in range(0, len(buf) // width, width):
            self.assertTrue(predicate.is_zero_sample(buf, i), f'{i}: {buf[i:i+width]}')

class TestFloatZeroSamplePredicate(unittest.TestCase):
    def test_zero_samples_fp32(self):
        self._do_test_zero_samples_float(4, np.float32)

    def test_zero_samples_fp64(self):
        self._do_test_zero_samples_float(8, np.float64)

    def _do_test_zero_samples_float(self, width: int, dtype: np.dtype):
        lim = cwd.FloatZeroSamplePredicate.DEFAULT_EPS * 0.9
        vals = np.random.uniform(-lim, +lim, 4000).astype(dtype)
        buf = vals.tobytes()
        predicate = cwd.FloatZeroSamplePredicate(width)
        for i in range(0, 4000):
            self.assertTrue(predicate.is_zero_sample(buf, i*width), f'{i}: {buf[i*width:i*width+width]}')

class TestRWaveReader(unittest.TestCase):
    def test_read(self):
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            w.writeframes(bytes(2 * 40000))
        buf.seek(0)
        reader = cwd.RWaveReader(cwd.WaveFormatParser(), buf)
        num_samples = reader.count_frames()
        self.assertEqual(40000, num_samples)
        pos = 0
        while (pos < num_samples):
            b = reader.read(777)
            pos += len(b)
        self.assertEqual(pos, 40000)

if __name__ == '__main__':
    cwd.LogConfigurator().configre()
    unittest.main()
