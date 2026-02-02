# coding: utf-8

import unittest
from r_framework.log import LogMixin

class TestRLogMixin(unittest.TestCase):
    class _LogMixinSubclass(LogMixin):
        LOGGER_PRFIX = 'r.test.log.'
        pass

    def test_get_logger(self):
        log_mixin = LogMixin()
        self.assertEqual('r.LogMixin', log_mixin.get_logger().name)

    def test_get_logger_for_subclass(self):
        log_mixin = self._LogMixinSubclass()
        self.assertEqual('r.test.log._LogMixinSubclass', log_mixin.get_logger().name)
