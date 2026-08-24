"""ParseDoc Timing utilities"""

import time
from contextlib import contextmanager
from typing import Dict


@contextmanager
def timing(label: str = ""):
    """Context manager that times a block and prints elapsed seconds."""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        if label:
            print(f"{label}: {elapsed:.2f}s")


class Timer:
    """Simple accumulator for stage timings."""

    def __init__(self):
        self.stages: Dict[str, float] = {}
        self._start = None
        self._label = None

    def start(self, label: str):
        self._label = label
        self._start = time.time()

    def stop(self):
        if self._start is not None and self._label is not None:
            self.stages[self._label] = time.time() - self._start
            self._start = None
            self._label = None

    def total(self) -> float:
        return sum(self.stages.values())
