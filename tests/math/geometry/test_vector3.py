import numpy as np

from tongsim.logger import get_logger
from tongsim.math.geometry import Vector3, geometry

_logger = get_logger("test")


def test_vector3_default():
    v = Vector3()
    assert v == Vector3(0.0, 0.0, 0.0)


def test_vector3_from_list():
    v = Vector3([1.0, 2.0, 3.0])
    assert v == Vector3(1.0, 2.0, 3.0)


def test_vector3_from_args():
    v = Vector3(1.0, 2.0, 3.0)
    assert v == Vector3(1.0, 2.0, 3.0)


def test_vector3_from_numpy():
    v = Vector3(np.array([1.0, 2.0, 3.0]))
    assert v == Vector3([1.0, 2.0, 3.0])


def test_vector3_copy_constructor():
    v1 = Vector3(1.0, 2.0, 3.0)
    v2 = Vector3(v1)
    assert v1 == v2


def test_vector3_add():
    v1 = Vector3(1.0, 2.0, 3.0)
    v2 = Vector3(4.0, 5.0, 6.0)
    result = v1 + v2
    result.__len__()
    assert result == Vector3([5.0, 7.0, 9.0])


def test_vector3_subtract():
    v1 = Vector3(5.0, 7.0, 9.0)
    v2 = Vector3(1.0, 2.0, 3.0)
    result = v1 - v2
    assert result == Vector3([4.0, 5.0, 6.0])


def test_vector3_multip():
    v = Vector3(1.0, 2.0, 3.0)
    result = v * 2
    assert result == Vector3([2.0, 4.0, 6.0])


def test_vector3_equality():
    v1 = Vector3([1.0, 2.0, 3.0])
    v2 = [1.0, 2.0, 3.0]
    v3 = Vector3()
    assert v1 == v2
    assert v1 != v3


def test_vector3_component_access():
    v = Vector3([1.0, 2.0, 3.0])
    assert v.x == 1.0
    assert v.y == 2.0
    assert v.z == 3.0
    assert np.allclose(v.xy, [1.0, 2.0])
    assert np.allclose(v.xz, [1.0, 3.0])
    assert np.allclose(v.xyz, [1.0, 2.0, 3.0])


def test_vector3_normalize():
    v = Vector3(3.0, 0.0, 4.0)
    normalized = geometry.normalize(v)
    assert np.allclose(geometry.length(normalized), 1.0)


def test_vector3_dot_cross():
    v1 = Vector3(1.0, 0.0, 0.0)
    v2 = Vector3(0.0, 1.0, 0.0)
    assert geometry.dot(v1, v2) == 0.0
    assert geometry.cross(v1, v2) == Vector3([0.0, 0.0, 1.0])
