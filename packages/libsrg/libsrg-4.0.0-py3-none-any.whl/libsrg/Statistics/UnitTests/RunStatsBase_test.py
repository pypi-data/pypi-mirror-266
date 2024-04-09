import unittest
from typing import Optional, Callable

from libsrg.Statistics.RunStatsBase import RunStatsBase


class RunStatsBase2(RunStatsBase):

    def __init__(self, name, callbacks: Optional[list[Callable]] = None):
        super().__init__(name, callbacks)
        self.sampled = None

    def process_sample(self):
        self.sampled = self._last_sample


class User:
    def __init__(self):
        self.s1 = RunStatsBase2("s1")
        self.s2 = RunStatsBase2("s2")


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.rec0 = None
        self.rec1 = None

    def cb0(self, record):
        self.rec0 = record

    def cb1(self, record):
        self.rec1 = record

    def test_something(self):
        user1 = User()
        self.assertIsNotNone(user1)
        self.assertEqual("s1", user1.s1.name())

        exp = [user1.s1, user1.s2]
        act = RunStatsBase.find_in_object(user1)
        print(act)
        self.assertEqual(exp, act)

    def test_callbacks(self):
        s1 = RunStatsBase2("s1")
        s1.sample(1)
        self.assertEqual(None, self.rec0)
        self.assertEqual(None, self.rec1)

        s1.register_callback(self.cb0)
        RunStatsBase.register_class_callback(self.cb1)
        s1.sample(2)
        self.assertIsNotNone(self.rec0)
        self.assertIsNotNone(self.rec1)


if __name__ == '__main__':
    unittest.main()
