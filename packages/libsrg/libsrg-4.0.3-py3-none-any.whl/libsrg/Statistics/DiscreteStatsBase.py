from collections import Counter
from typing import Optional, Callable, Any

from libsrg.Statistics.RunStatsBase import RunStatsBase


class DiscreteStatsBase(RunStatsBase):
    class_callbacks: list[Callable] = []

    def __init__(self, name, callbacks: Optional[list[Callable]] = None):
        super().__init__(name=name, callbacks=callbacks)
        self.counter = Counter()

    def get_all_callbacks(self) -> list[Callable]:
        lst = super().get_all_callbacks()
        lst.extend(DiscreteStatsBase.class_callbacks)
        return lst

    def sample(self, value: Any, sample_time: Optional[float] = None) -> bool:
        first = super().sample(value=value, sample_time=sample_time)
        self.counter[value] += 1
        return first

    def reset(self):
        super().reset()
        self.counter.clear()

    def counts(self) -> Counter:
        return self.counter.copy()

    def count_for(self, value: Any) -> int:
        return self.counter[value]

    def most_common(self, n: int) -> list[tuple[Any, int]]:
        return self.counter.most_common(n)

    def most_common_as_str(self, n: int) -> str:
        return str(self.counter.most_common(n))
