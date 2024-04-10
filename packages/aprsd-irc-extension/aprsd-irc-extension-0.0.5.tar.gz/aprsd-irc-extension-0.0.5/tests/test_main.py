import sys
import unittest


if sys.version_info >= (3, 2):
    from unittest import mock  # noqa
else:
    from unittest import mock  # noqa


class TestMain(unittest.TestCase):

    def test_nothing(self):
        pass
