import random
import unittest
from time import time
from typing import Any

from libsrg.Statistics.AnalogStatsCumulative import AnalogStatsCumulative
from libsrg.Statistics.AnalogStatsFading import AnalogStatsFading

# force reproducible random data
my_random = random.Random()
my_random.seed(42)

gdata_mu = 100.
gdata_sigma = 10.
gdata = [my_random.gauss(mu=gdata_mu, sigma=gdata_sigma) for _ in range(10000)]


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # with alpha and beta set to 1, weighted and non-weighted stats should match
        r = AnalogStatsFading("varname", alpha=1, beta=1)
        self.assertEqual(0, r._sample_count)
        self.assertEqual("varname", r.name())

        r.sample(4)
        self.assertEqual(1, r._sample_count)

        r.sample(5)
        r.sample(6)

        self.assertEqual(3, r._sample_count)
        self.assertAlmostEqual(3., r._wsum_weight)

        self.assertAlmostEqual(15., r._wsum_samples)

        self.assertAlmostEqual(5., r.mean())

        ex: float = sum([4. * 4., 5. * 5., 6. * 6.])
        self.assertAlmostEqual(ex, r._wsum_samples_sq)

        ex: float = sum([4 * 4, 5 * 5, 6 * 6]) / 3.
        print(f"{ex=}")
        self.assertAlmostEqual(ex, r.mean_squared())
        print(r)

    def test_random_0_9(self):
        self.random_inner(alpha=0.9)

    def test_random_0_99(self):
        self.random_inner(alpha=0.99)

    def test_random_0_999(self):
        self.random_inner(alpha=0.999)

    def random_inner(self, alpha=0.99):
        print("---------------------")
        t0 = time()
        r = AnalogStatsFading("random1", alpha=alpha)
        for i, s in enumerate(gdata):
            r.sample(s, sample_time=(t0 + i))
        self.assertAlmostEqual(gdata_mu, r.mean(), delta=2.5)
        self.assertAlmostEqual(gdata_sigma, r.sd(), delta=2.5)
        print(f"{r._sample_count=} {r._alpha=} {r._beta=}")
        print(f"{r._wsum_weight=}")
        print(r)
        print("---------------------")

    def test_weights(self):
        r = AnalogStatsFading("random1", alpha=0.95)
        r.sample(100., weight=100, sd=7)

        self.assertAlmostEqual(100., r.mean())
        self.assertAlmostEqual(7., r.sd())

    def test_vs_cumulative(self):
        print("---------------------")
        r = AnalogStatsFading("fading", alpha=1.0, beta=1.0)
        rc = AnalogStatsCumulative("cumulative")
        for i, s in enumerate(gdata):
            r.sample(s)
            rc.sample(s)
            self.assertAlmostEqual(r._wsum_samples, rc._sum_samples)
            self.assertAlmostEqual(r._wsum_samples_sq, rc._sum_samples_sq)
            self.assertAlmostEqual(r._wsum_weight, rc._sample_count)

        self.assertAlmostEqual(rc.mean(), r.mean())
        self.assertAlmostEqual(rc.mean_squared(), r.mean_squared())
        self.assertAlmostEqual(rc.variance(), r.variance())
        self.assertAlmostEqual(rc.sd(), r.sd())

        self.assertAlmostEqual(gdata_mu, rc.mean(), delta=2.5)
        self.assertAlmostEqual(gdata_sigma * gdata_sigma, rc.variance(), delta=2.5)
        self.assertAlmostEqual(gdata_sigma, rc.sd(), delta=2.5)
        self.assertAlmostEqual(gdata_mu, r.mean(), delta=2.5)
        self.assertAlmostEqual(gdata_sigma, r.sd(), delta=2.5)
        print(f"{r._sample_count=} {r._alpha=} {r._beta=}")
        print(f"{r._wsum_weight=}")
        print(r)
        print("---------------------")

    def callback(self, record):
        self.record = record

    def test_callback(self):
        t0 = time()
        r = AnalogStatsFading("callback", callbacks=[self.callback])
        self.record: dict[str, Any] | None = None
        r.sample(1000, sample_time=t0)
        print(self.record)
        self.assertIsNotNone(self.record)
        self.assertAlmostEqual(1000., self.record["value"])
        print(r)


if __name__ == '__main__':
    unittest.main()
