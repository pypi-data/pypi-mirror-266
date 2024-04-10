import math
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any

from libsrg.Statistics.RunStatsBase import RunStatsBase


class AnalogStatsBase(RunStatsBase, ABC):
    class_callbacks: list[Callable] = []

    def __init__(self, name, callbacks: Optional[list[Callable]] = None):
        super().__init__(name=name, callbacks=callbacks)
        self._min_sample: Any = None
        self._max_sample: Any = None

    def get_all_callbacks(self) -> list[Callable]:
        lst = super().get_all_callbacks()
        lst.extend(AnalogStatsBase.class_callbacks)
        return lst

    def sample_bool(self, value: bool, sample_time: Optional[float] = None):
        super().sample(value=(1 if value else 0), sample_time=sample_time)

    def sample(self, value: Any, sample_time: Optional[float] = None) -> bool:
        first = super().sample(value=value, sample_time=sample_time)
        if first or value > self._max_sample:
            self._max_sample = value
        if first or value < self._min_sample:
            self._min_sample = value
        return first

    def reset(self):
        super().reset()
        self._min_sample: Any = None
        self._max_sample: Any = None

    @abstractmethod
    def mean(self) -> float:
        return math.nan

    @abstractmethod
    def mean_squared(self) -> float:
        return math.nan

    def root_mean_squared(self) -> float:
        try:
            return math.sqrt(self.mean_squared())
        except ArithmeticError:
            return math.nan

    def sd(self):
        try:
            return math.sqrt(self.variance())
        except ArithmeticError:
            return math.nan

    def variance(self) -> float:
        _mean = self.mean()
        _var = self.mean_squared() - _mean * _mean
        # clamp variance in case of accumulated arithmatic errors
        return max(_var, 0.0)

    def min_sample(self):
        return self._min_sample

    def max_sample(self):
        return self._max_sample
