"""
Helpers for progress bars and ETA estimation.
"""

import time


# ----------------------------------------------------------
# Progress
# ----------------------------------------------------------
class Progress:
    "A class to measure the progress of an algorithm"

    def __init__(self, x0=0, N=10):
        self.n0 = 0
        self.n1 = 0
        self.x = x0
        self.N = N
        self.samples = []
        self.t0 = 0
        self.t1 = 0
        self.freq = 5
        self.data = {}

    def update(self, n=1, force=False, **data):
        "Update the progress"
        t1 = time.time()
        self.data.update(data)

        self.x += n
        sample = t1, self.x
        self.samples.append(sample)

        if force or t1 > self.t1:
            self.samples = self.samples[100:]
            elapsed = t1 - self.t0
            speed = self.n1 / elapsed
            self.t0 = t1
            self.t1 = t1 + self.freq
            self.n1 = 0
            print(f"Speed: {speed} items/sec: {self.data}: n: {n}, x: {self.x}")
