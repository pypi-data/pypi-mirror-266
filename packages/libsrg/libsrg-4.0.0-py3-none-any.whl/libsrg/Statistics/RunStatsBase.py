from abc import ABC
from time import time
from typing import Optional, Callable, Self, Any


# General note:
#   for classmethods defined in the baseclass, if called on a subclass,
#
class RunStatsBase(ABC):
    class_callbacks: list[Callable] = []

    @classmethod
    def register_class_callback(cls, callback: Callable) -> list[Callable]:
        cls.class_callbacks.append(callback)
        return cls.class_callbacks

    @classmethod
    def unregister_class_callback(cls, callback: Callable):
        if callback in cls.class_callbacks:
            cls.class_callbacks.remove(callback)

    def __init__(self, name, callbacks: Optional[list[Callable]] = None):
        self._sample_count = 0
        self._last_sample = None
        self._name = name
        self.instance_callbacks = callbacks if callbacks else []
        self._time_first_sample: Optional[float] = None
        self._time_last_sample: float = 0

    def reset(self) -> None:
        """
        Clear all statistics
        if overriden by subclass, call super
        """
        self._time_last_sample = None
        self._last_sample = None
        self._sample_count = 0

    def get_all_callbacks(self) -> list[Callable]:
        lst = []
        lst.extend(RunStatsBase.class_callbacks)
        lst.extend(self.instance_callbacks)
        return lst

    def sample(self, value: Any, sample_time: Optional[float] = None) -> bool:
        """

        :param value:
        :param sample_time:
        :return: True if first sample after reset
        """
        self._time_last_sample = sample_time if sample_time else time()
        self._last_sample = value
        self._sample_count += 1
        self.notify()
        first = self._sample_count == 1
        if first:
            self._time_first_sample = sample_time
        return first

    def notify(self):
        all_callbacks = self.get_all_callbacks()
        if len(all_callbacks) > 0:
            record = {"name": self._name,
                      "count": self._sample_count,
                      "value": self._last_sample,
                      "time": self._time_last_sample}
            for callback in all_callbacks:
                callback(record)

    def name(self) -> str:
        return self._name

    def count(self) -> int:
        return self._sample_count

    @classmethod
    def find_in_object(cls, obj: Any, tgt_class=None, nosort: bool = False) -> list[Self]:
        """
        Given obj, find all instances variables which are an instance of tgt_class

        Note that even though this classmethod is defined on the base class, it can be
        called on any subclass, and will (by default) find instances of that subclass

        :param nosort: if set true, return list unsorted
        :param obj: an object whose __dict__ may contain instances of tgt_class
        :param tgt_class: if not specified, defaults to class (possibly derived) on which this method is called
        :return:
        """
        if tgt_class is None:
            tgt_class = cls
        stats = [v for k, v in obj.__dict__.items() if isinstance(v, tgt_class)]
        if not nosort:
            stats.sort()
        return stats

    def __lt__(self, other: Self | None) -> bool:
        """Allow sorting by name"""
        return self._name < other._name

    def register_callback(self, callback: Callable):
        self.instance_callbacks.append(callback)

    def unregister_callback(self, callback: Callable):
        if callback in self.instance_callbacks:
            self.instance_callbacks.remove(callback)

    def last_sample(self) -> Any:
        return self._last_sample
