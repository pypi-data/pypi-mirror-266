from __future__ import annotations

import datetime
import math
import time
import typing as t

DEFAULT_TIMER_PRECISION: t.Final = 2


class Timer:
    def __init__(self, precision: int = DEFAULT_TIMER_PRECISION) -> None:
        self.precision = precision
        self.start: float | None = None
        self.end: float | None = None

    def __enter__(self) -> Timer:
        self.start = time.time()
        return self

    def __exit__(self, *args: t.Any) -> None:
        self.end = time.time()

    def __str__(self) -> str:
        return self.verbose()

    def __repr__(self) -> str:
        return f"<Timer [start={self.start}, end={self.end}]>"

    def verbose(self) -> str:
        ms, seconds = math.modf(self.elapsed)
        ms_part = round(ms, self.precision) * 10**self.precision
        return f"{datetime.timedelta(seconds=seconds)}.{int(ms_part)}"

    @property
    def elapsed(self) -> float:
        if not self.start:
            return 0.0
        return (self.end or time.time()) - self.start
