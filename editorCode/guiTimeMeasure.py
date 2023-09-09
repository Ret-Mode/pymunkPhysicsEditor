import time

from collections import namedtuple
from typing import NamedTuple


class TimeMeasure:
    frame: NamedTuple("frame", [("update", float), ("draw", float), ("sum", float)]) = namedtuple("frame", "update draw sum")
    draw = [0]
    update = [0]
    current = 0
    size = 1

    @staticmethod
    def resize(size):
        assert size > 0
        TimeMeasure.size = 1
        TimeMeasure.draw = [0 for i in range(size)]
        TimeMeasure.update = [0 for i in range(size)]
        TimeMeasure.current = 0
        TimeMeasure.size = size

    @staticmethod
    def measureUpdate(measuredFunc):
        def decorator(measuredSelf, *args, **kwargs):
            start: float = time.time()
            current: int = TimeMeasure.current
            val = measuredFunc(measuredSelf, *args, **kwargs)
            duration: float = time.time() - start
            further: int = (current + 1) % TimeMeasure.size
            #TimeMeasure.draw[further] = 0
            TimeMeasure.update[current] = duration
            TimeMeasure.current = further
            return val
        return decorator
    
    @staticmethod
    def measureDraw(measuredFunc):
        def decorator(measuredSelf, *args, **kwargs):
            start: float = time.time()
            current: int = TimeMeasure.current
            val = measuredFunc(measuredSelf, *args, **kwargs)
            duration: float = time.time() - start 
            TimeMeasure.draw[current] = duration
            TimeMeasure.clearDraw(current, duration)
            return val
        return decorator
    
    @staticmethod
    def clearDraw(current, val: float) -> None:
        while (val > 1.0/60.0):
            current: int = (current + 1) % TimeMeasure.size
            TimeMeasure.draw[current] = 0
            val -= 1.0/60.0

    @staticmethod
    def getFrame(frame: int) -> NamedTuple("frame", [("update", float), ("draw", float), ("sum", float)]):
        u = TimeMeasure.update[frame]
        d = TimeMeasure.draw[frame]
        return TimeMeasure.frame(u,d,u+d)

