import unittest

from libsrg.Statistics.AnalogStatsBase import AnalogStatsBase
from libsrg.Statistics.RunStatsBase import RunStatsBase


class Concrete(AnalogStatsBase):

    def mean_squared(self) -> float:
        pass

    def root_mean_squared(self) -> float:
        pass

    def variance(self) -> float:
        pass

    def sd(self):
        pass

    def mean(self) -> float:
        pass


class ConcreteB(RunStatsBase):
    pass


class User:
    def __init__(self):
        self.s1 = Concrete("s1")
        self.s2 = Concrete("s2")
        self.b1 = ConcreteB("b1")


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.rec0 = None
        self.rec1 = None
        self.rec2 = None

    def cb0(self, record):
        self.rec0 = record

    def cb1(self, record):
        self.rec1 = record

    def cb2(self, record):
        self.rec2 = record

    def test_constructor(self):
        user1 = User()
        self.assertIsNotNone(user1)
        self.assertEqual("s1", user1.s1.name())

        exp = [user1.s1, user1.s2]
        act = AnalogStatsBase.find_in_object(user1)
        print(act)
        self.assertEqual(exp, act)

    def test_callbacks(self):
        s1 = Concrete("s1")
        s1.sample(1)
        self.assertEqual(None, self.rec0)
        self.assertEqual(None, self.rec1)

        lst = s1.get_all_callbacks()
        self.assertEqual(0, len(lst))

        s1.register_callback(self.cb0)
        lst = s1.get_all_callbacks()
        self.assertEqual(1, len(lst))

        RunStatsBase.register_class_callback(self.cb1)
        lst = s1.get_all_callbacks()
        self.assertEqual(2, len(lst))

        AnalogStatsBase.register_class_callback(self.cb2)
        lst = s1.get_all_callbacks()
        self.assertEqual(3, len(lst))

        s1.sample(2)
        self.assertIsNotNone(self.rec0)
        self.assertIsNotNone(self.rec1)
        self.assertIsNotNone(self.rec2)

        # a new Concrete object should get 2 class callbacks
        s2 = Concrete("s2")
        lst = s2.get_all_callbacks()
        self.assertEqual(2, len(lst))

        # a new ConcreteB object should get 1 class callbacks
        s_b = ConcreteB("sB")
        lst = s_b.get_all_callbacks()
        self.assertEqual(1, len(lst))

    def test_finder(self):
        u = User()

        lst = RunStatsBase.find_in_object(u)
        self.assertEqual(3, len(lst))

        lst = AnalogStatsBase.find_in_object(u)
        self.assertEqual(2, len(lst))


if __name__ == '__main__':
    unittest.main()
