from wav_logic import (
    _PcmIntZeroSoundPredicate, # type: ignore
    _PcmInt8ZeroSoundPredicate, # type: ignore
    _FloatZeroSoundPredicate, # type: ignore
)

import numpy as np
import random
import unittest


class TestPcmIntZeroSoundPredicate(unittest.TestCase):

    # ---- x >= 0 ----

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
            buf[i * width] = random.randint(0, 0xFF)
        predicate = _PcmIntZeroSoundPredicate(width, -10.0)
        for i in range(0, len(buf) // width, width):
            self.assertTrue(
                predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i:i+width]}"
            )

    def test_positive_zero_samples_int16_false(self):
        self._do_test_positive_zero_samples_int_false(2)

    def test_positive_zero_samples_int24_false(self):
        self._do_test_positive_zero_samples_int_false(3)

    def test_positive_zero_samples_int32_false(self):
        self._do_test_positive_zero_samples_int_false(4)

    def _do_test_positive_zero_samples_int_false(self, width: int):
        count = 4000
        buf = bytearray(count * width)
        for i in range(0, count):
            buf[i * width] = random.randint(1, 0xFF)
        predicate = _PcmIntZeroSoundPredicate(width, -200.0)
        for i in range(0, len(buf) // width, width):
            self.assertFalse(
                predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i:i+width]}"
            )

    def test_positive_zero_samples_int16_false_upper_bytes(self):
        self._do_test_positive_zero_samples_int_false_upper_bytes(2)

    def test_positive_zero_samples_int24_false_upper_bytes(self):
        self._do_test_positive_zero_samples_int_false_upper_bytes(3)

    def test_positive_zero_samples_int32_false_upper_bytes(self):
        self._do_test_positive_zero_samples_int_false_upper_bytes(4)

    def _do_test_positive_zero_samples_int_false_upper_bytes(self, width: int):
        count = 4000
        buf = bytearray(count * width)
        for i in range(0, count):
            buf[i * width + random.randint(1, width - 1)] = random.randint(1, 0xFF)
        predicate = _PcmIntZeroSoundPredicate(width, -10.0)
        for i in range(0, len(buf) // width, width):
            self.assertFalse(
                predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i:i+width]}"
            )

    # ---- x <= 0 ----

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
            # excludes 0, because 0xFF...00 is -256 (not -255) as a signed integer.
            buf[i * width] = random.randint(1, 0xFF)
        predicate = _PcmIntZeroSoundPredicate(width, -10.0)
        for i in range(0, len(buf) // width, width):
            self.assertTrue(
                predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i:i+width]}"
            )

    def test_negative_zero_samples_int16_false(self):
        self._do_test_negative_zero_samples_int_false(2)

    def test_negative_zero_samples_int24_false(self):
        self._do_test_negative_zero_samples_int_false(3)

    def test_negative_zero_samples_int32_false(self):
        self._do_test_negative_zero_samples_int_false(4)

    def _do_test_negative_zero_samples_int_false(self, width: int):
        count = 4000
        buf = bytearray([0xFF] * count * width)
        for i in range(0, count):
            buf[i * width] = random.randint(0, 0xFF)
        predicate = _PcmIntZeroSoundPredicate(width, -200.0)
        for i in range(0, len(buf) // width, width):
            self.assertFalse(
                predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i:i+width]}"
            )

    def test_negative_zero_samples_int16_false_upper_bytes(self):
        self._do_test_negative_zero_samples_int_false_upper_bytes(2)

    def test_negative_zero_samples_int24_false_upper_bytes(self):
        self._do_test_negative_zero_samples_int_false_upper_bytes(3)

    def test_negative_zero_samples_int32_false_upper_bytes(self):
        self._do_test_negative_zero_samples_int_false_upper_bytes(4)

    def _do_test_negative_zero_samples_int_false_upper_bytes(self, width: int):
        count = 4000
        buf = bytearray([0xFF] * (count * width))
        for i in range(0, count):
            # 0x00FF causes int16 predicate to return true
            buf[i * width + random.randint(1, width - 1)] = random.randint(1, 0xFE)
        predicate = _PcmIntZeroSoundPredicate(width, -10.0)
        for i in range(0, len(buf) // width, width):
            self.assertFalse(
                predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i:i+width]}"
            )


class TestPcmInt8ZeroSoundPredicate(unittest.TestCase):
    def test_true_cases(self):
        count = 4000
        buf = bytearray(count)
        for i in range(0, count):
            buf[i] = random.randint(0x80, 0xFF)
        predicate = _PcmInt8ZeroSoundPredicate(-0.01)
        for i in range(0, len(buf)):
            self.assertTrue(predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i]}")

    def test_false_cases(self):
        count = 4000
        buf = bytearray([0xFF] * count)
        for i in range(0, count):
            v = random.randint(0, 0xFF)
            if 0x80 == v:
                continue
            buf[i] = v
        predicate = _PcmInt8ZeroSoundPredicate(-200)
        for i in range(0, len(buf)):
            self.assertFalse(predicate.is_zero_sound_sample(buf, i), f"{i}: {buf[i]}")


class TestFloatZeroSoundPredicate(unittest.TestCase):
    def test_zero_samples_fp32(self):
        self._do_test_zero_samples_float(4, np.dtype(np.float32))

    def test_zero_samples_fp64(self):
        self._do_test_zero_samples_float(8, np.dtype(np.float64))

    def _do_test_zero_samples_float(self, width: int, dtype: np.dtype[np.floating]):
        lim = 0.99
        vals = np.random.uniform(-lim, +lim, 4000).astype(dtype)
        buf = vals.tobytes()
        predicate = _FloatZeroSoundPredicate(width, -0.01)
        for i in range(0, 4000):
            self.assertTrue(
                predicate.is_zero_sound_sample(buf, i * width),
                f"{i}: {buf[i*width:i*width+width]}",
            )

    def test_zero_samples_fp32_false(self):
        self._do_test_zero_samples_float_false(4, np.dtype(np.float32))

    def test_zero_samples_fp64_false(self):
        self._do_test_zero_samples_float_false(8, np.dtype(np.float64))

    def _do_test_zero_samples_float_false(self, width: int, dtype: np.dtype[np.floating]):
        # -20dB -> 0.1x
        x = np.random.uniform(1e-9, 1e-2, 4000)
        sign = np.random.choice([1, -1], size=x.shape)
        x *= sign
        buf = x.astype(dtype).tobytes()
        predicate = _FloatZeroSoundPredicate(width, -200)
        for i in range(0, 4000):
            self.assertFalse(
                predicate.is_zero_sound_sample(buf, i * width),
                f"{i}: {buf[i*width:i*width+width]}",
            )
