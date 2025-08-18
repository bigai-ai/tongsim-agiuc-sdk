import time

import numpy as np

from tongsim.logger import get_logger
from tongsim.math.geometry import Vector3, geometry

_logger = get_logger("performance")


class SimpleVector3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return SimpleVector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return SimpleVector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z


def benchmark(name, fn, repeat=1):
    start = time.perf_counter()
    for _ in range(repeat):
        fn()
    end = time.perf_counter()
    _logger.info(f"{name:<30}: {end - start:.6f} 秒")


# ========== Multiply ==========


def test_tongsim_multiply(num=1_000_000):
    v1 = Vector3(1.0, 2.0, 3.0)
    v2 = Vector3(4.0, 5.0, 6.0)
    benchmark(
        f"TongSim vector3 multiply {num} times", lambda: [v1 * v2 for _ in range(num)]
    )


def test_simple_multiply(num=1_000_000):
    v1 = SimpleVector3(1.0, 2.0, 3.0)
    v2 = SimpleVector3(4.0, 5.0, 6.0)
    benchmark(
        f"Simple vector3  multiply {num} times",
        lambda: [
            SimpleVector3(v1.x * v2.x, v1.y * v2.y, v1.z * v2.z) for _ in range(num)
        ],
    )


def test_numpy_multiply(num=1_000_000):
    v1 = np.array([1.0, 2.0, 3.0])
    v2 = np.array([4.0, 5.0, 6.0])
    benchmark(
        f"NumPy vector3  multiply {num} times", lambda: [v1 * v2 for _ in range(num)]
    )


# ========== Add ==========


def test_tongsim_add(num=1_000_000):
    v1 = Vector3(1.0, 2.0, 3.0)
    v2 = Vector3(4.0, 5.0, 6.0)
    benchmark(f"TongSim vector3 add {num} times", lambda: [v1 + v2 for _ in range(num)])


def test_simple_add(num=1_000_000):
    v1 = SimpleVector3(1.0, 2.0, 3.0)
    v2 = SimpleVector3(4.0, 5.0, 6.0)
    benchmark(f"Simple vector3 add {num} times", lambda: [v1 + v2 for _ in range(num)])


def test_numpy_add(num=1_000_000):
    v1 = np.array([1.0, 2.0, 3.0])
    v2 = np.array([4.0, 5.0, 6.0])
    benchmark(f"NumPy vector3 add {num} times", lambda: [v1 + v2 for _ in range(num)])


# ========== Dot ==========


def test_tongsim_dot(num=1_000_000):
    v1 = Vector3(1.0, 2.0, 3.0)
    v2 = Vector3(4.0, 5.0, 6.0)
    benchmark(
        f"TongSim vector3 dot {num} times",
        lambda: [geometry.dot(v1, v2) for _ in range(num)],
    )


def test_simple_dot(num=1_000_000):
    v1 = SimpleVector3(1.0, 2.0, 3.0)
    v2 = SimpleVector3(4.0, 5.0, 6.0)
    benchmark(
        f"Simple vector3 dot {num} times", lambda: [v1.dot(v2) for _ in range(num)]
    )


def test_numpy_dot(num=1_000_000):
    v1 = np.array([1.0, 2.0, 3.0])
    v2 = np.array([4.0, 5.0, 6.0])
    benchmark(
        f"NumPy vector3 dot {num} times", lambda: [np.dot(v1, v2) for _ in range(num)]
    )
