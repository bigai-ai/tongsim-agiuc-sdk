"""
tongsim.math.geometry.type
"""

# ruff: noqa: N812
from pyglm import glm as _glm
from pyglm.glm import mat4 as Mat4
from pyglm.glm import mat4_cast, translate
from pyglm.glm import quat as Quaternion
from pyglm.glm import scale as glm_scale
from pyglm.glm import vec2 as Vector2
from pyglm.glm import vec3 as Vector3

__all__ = ["Box", "Mat4", "Pose", "Quaternion", "Transform", "Vector2", "Vector3"]


class Pose:
    """
    Pose 类，提供 location 和 rotation 的轻量级只读结构封装，用于位置和旋转统一传递。
    """

    __slots__ = ("location", "rotation")

    def __init__(
        self, location: Vector3 | None = None, rotation: Quaternion | None = None
    ):
        self.location = location if location is not None else Vector3(0.0, 0.0, 0.0)
        self.rotation = (
            rotation if rotation is not None else Quaternion(1.0, 0.0, 0.0, 0.0)
        )

    def __repr__(self) -> str:
        return f"Pose(location={self.location}, rotation={self.rotation})"

    def copy(self) -> "Pose":
        """
        返回该 Pose 的 deepcopy。
        """
        return Pose(Vector3(self.location), Quaternion(self.rotation))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Pose)
            and self.location == other.location
            and self.rotation == other.rotation
        )

    def to_transform(self) -> "Transform":
        """
        将当前 Pose 转换为 Transform 。
        """
        return Transform(self.location, self.rotation, Vector3(1.0, 1.0, 1.0))

    def to_list(self) -> list[float]:
        """
        返回当前 Pose 的数据列表。
        """
        return [
            self.location.x,
            self.location.y,
            self.location.z,
            self.rotation.x,
            self.rotation.y,
            self.rotation.z,
            self.rotation.w,
        ]


class Transform:
    """
    Transform 类，封装 location、rotation、scale 三个字段。

    提供统一的空间变换数据结构，与 Unreal Engine Transform 对齐。
    """

    __slots__ = ("location", "rotation", "scale")

    def __init__(
        self,
        location: Vector3 | None = None,
        rotation: Quaternion | None = None,
        scale: Vector3 | None = None,
    ):
        self.location = location if location is not None else Vector3(0.0, 0.0, 0.0)
        self.rotation = (
            rotation if rotation is not None else Quaternion(1.0, 0.0, 0.0, 0.0)
        )
        self.scale = scale if scale is not None else Vector3(1.0, 1.0, 1.0)

    def __repr__(self) -> str:
        return (
            f"Transform(location={self.location}, "
            f"rotation={self.rotation}, scale={self.scale})"
        )

    def copy(self) -> "Transform":
        """
        返回当前 Transform 的 deepcopy。
        """
        return Transform(
            Vector3(self.location),
            Quaternion(self.rotation),
            Vector3(self.scale),
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Transform)
            and self.location == other.location
            and self.rotation == other.rotation
            and self.scale == other.scale
        )

    def __mul__(self, other: "Transform") -> "Transform":
        """
        组合两个 Transform（右乘），返回新的 Transform。
        相当于先应用 `other`，再应用 `self`。

        Args:
            other (Transform): 要与当前变换组合的另一个 Transform。

        Returns:
            Transform: 组合后的新变换。
        """
        if not isinstance(other, Transform):
            return NotImplemented

        # 变换矩阵相乘
        m = self.to_matrix() * other.to_matrix()
        # print (m)

        # 从矩阵提取平移
        loc = Vector3(m[3].x, m[3].y, m[3].z)

        # 提取 scale
        sx = _glm.length(Vector3(m[0].x, m[0].y, m[0].z))
        sy = _glm.length(Vector3(m[1].x, m[1].y, m[1].z))
        sz = _glm.length(Vector3(m[2].x, m[2].y, m[2].z))
        scale = Vector3(sx, sy, sz)

        # 提取 rotation（需要先去除 scale）
        rot_mat = Mat4(m)
        rot_mat[0] /= sx
        rot_mat[1] /= sy
        rot_mat[2] /= sz
        rot = _glm.quat_cast(rot_mat)

        return Transform(loc, rot, scale)

    def to_matrix(self) -> Mat4:
        """
        返回当前 Transform 对应的 4x4 仿射变换矩阵。
        顺序为: scale → rotate → translate。
        """

        t = translate(Mat4(1.0), self.location)
        r = mat4_cast(self.rotation)
        s = glm_scale(Mat4(1.0), self.scale)
        return t * r * s  # 注意矩阵右乘顺序

    def transform_vector3(self, point: Vector3) -> Vector3:
        """
        将当前 Transform 应用于一个 3D 点，返回变换后的结果。
        """
        m = self.to_matrix()
        p = m * _glm.vec4(point, 1.0)  # 使用齐次坐标
        return Vector3(p.x, p.y, p.z)

    def inverse(self) -> "Transform":
        """
        返回当前 Transform 的逆变换。
        注意: 先逆 scale、再逆 rotate、最后逆 translate。
        """
        if self.scale.x == 0 or self.scale.y == 0 or self.scale.z == 0:
            raise ValueError(f"Cannot invert Transform with zero scale: {self.scale}")
        inv_scale = Vector3(
            1.0 / self.scale.x,
            1.0 / self.scale.y,
            1.0 / self.scale.z,
        )
        inv_rot = _glm.inverse(self.rotation)
        inv_loc = -(inv_rot * (inv_scale * self.location))
        return Transform(inv_loc, inv_rot, inv_scale)


class Box:
    """
    Box 类，封装了一个 3D 轴对齐包围盒 (AABB)，包含最小值和最大值。
    提供了对 Box 的常见操作，比如包含检查、扩展、交集计算等。

    Attributes:
        min (Vector3): 包围盒的最小点（x, y, z 坐标最小）。
        max (Vector3): 包围盒的最大点（x, y, z 坐标最大）。
    """

    __slots__ = ("max", "min")

    def __init__(self, min: Vector3 | None = None, max: Vector3 | None = None):
        """
        初始化 Box 类，最小值和最大值默认为原点和单位立方体。
        """
        self.min = min if min is not None else Vector3(0.0, 0.0, 0.0)
        self.max = max if max is not None else Vector3(1.0, 1.0, 1.0)

    def __repr__(self) -> str:
        return f"Box(min={self.min}, max={self.max})"

    def copy(self) -> "Box":
        """
        返回当前 Box 的 deepcopy。

        Returns:
            Box: 拷贝对象。
        """
        return Box(Vector3(self.min), Vector3(self.max))

    def __eq__(self, other: object) -> bool:
        """
        判断当前 Box 是否与另一个 Box 相等。

        Returns:
            bool: 是否在相等。
        """
        return (
            isinstance(other, Box) and self.min == other.min and self.max == other.max
        )

    def extend(self, point: Vector3) -> None:
        """
        扩展当前 Box，包含给定的点。最小值和最大值将会更新以包含该点。

        Args:
            point (Vector3): 要扩展的点
        """
        self.min = Vector3(
            min(self.min.x, point.x), min(self.min.y, point.y), min(self.min.z, point.z)
        )
        self.max = Vector3(
            max(self.max.x, point.x), max(self.max.y, point.y), max(self.max.z, point.z)
        )

    def intersect(self, other: "Box") -> "Box":
        """
        返回当前 Box 和另一个 Box 的交集（如果存在）。
        如果交集为空，则返回一个min和max均为零点的Box。

        Args:
            other (Box): 要判断的Box。

        Returns:
            bool: 是否在内部。
        """
        new_min = Vector3(
            max(self.min.x, other.min.x),
            max(self.min.y, other.min.y),
            max(self.min.z, other.min.z),
        )
        new_max = Vector3(
            min(self.max.x, other.max.x),
            min(self.max.y, other.max.y),
            min(self.max.z, other.max.z),
        )

        # 如果交集为空，返回一个为0的Box
        if new_min.x > new_max.x or new_min.y > new_max.y or new_min.z > new_max.z:
            return Box(Vector3(), Vector3())

        return Box(new_min, new_max)

    def contains_point(self, point: Vector3) -> bool:
        """
        判断当前 Box 是否包含一个给定的点。

        Args:
            point (Vector3): 要判断的点。

        Returns:
            bool: 是否在内部。
        """
        return (
            self.min.x <= point.x <= self.max.x
            and self.min.y <= point.y <= self.max.y
            and self.min.z <= point.z <= self.max.z
        )

    def to_list(self) -> list[float]:
        """
        返回当前 Box 的数据列表：min 和 max 的 x, y, z 值。

        Returns:
            list[float]: 转为list表示。
        """
        return [self.min.x, self.min.y, self.min.z, self.max.x, self.max.y, self.max.z]

    def center(self) -> Vector3:
        """
        返回 Box 的中心点。

        Returns:
            Vector3: 中心点坐标。
        """
        return (self.min + self.max) * 0.5

    def extent(self) -> Vector3:
        """
        返回 Box 的尺寸（宽、高、深）。

        Returns:
            Vector3: 中心点坐标。
        """
        return Vector3(
            self.max.x - self.min.x, self.max.y - self.min.y, self.max.z - self.min.z
        )

    def volume(self) -> float:
        """
        返回 Box 的体积。
        """
        dimensions = self.extent()
        return dimensions.x * dimensions.y * dimensions.z
