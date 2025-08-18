import math

from pyglm import glm as _glm

from .type import Quaternion, Vector3

__all__ = [
    "calc_camera_look_at_rotation",
    "cross",
    "decode_voxel",
    "degrees_to_radians",
    "distance",
    "dot",
    "euler_to_quaternion",
    "length",
    "lerp",
    "normalize",
    "quaternion_to_euler",
    "radians_to_degrees",
]


# 从 glm 中继承的方法:
dot = _glm.dot
cross = _glm.cross
normalize = _glm.normalize
length = _glm.length
lerp = _glm.lerp


# 自定义方法:


def degrees_to_radians(value: float | Vector3) -> float | Vector3:
    """
    将角度值转换为弧度。

    Args:
        value (float | Vector3): 单个角度值或角度制的 Vector3。

    Returns:
        float | Vector3: 转换后的弧度值。
    """
    if isinstance(value, Vector3):
        return Vector3(
            math.radians(value.x),
            math.radians(value.y),
            math.radians(value.z),
        )
    return math.radians(value)


def radians_to_degrees(value: float | Vector3) -> float | Vector3:
    """
    将弧度值转换为角度。

    Args:
        value (float | Vector3): 单个弧度值或弧度制的 Vector3。

    Returns:
        float | Vector3: 转换后的角度值。
    """
    if isinstance(value, Vector3):
        return Vector3(
            math.degrees(value.x),
            math.degrees(value.y),
            math.degrees(value.z),
        )
    return math.degrees(value)


def euler_to_quaternion(euler: Vector3, is_degree: bool = True) -> Quaternion:
    """
    将欧拉角（roll, pitch, yaw）转换为四元数，默认单位为角度。

    使用 Unreal Engine 的 ZYX 旋转顺序：
    - Roll：绕 X 轴
    - Pitch：绕 Y 轴
    - Yaw：绕 Z 轴

    Args:
        euler (Vector3): 欧拉角，(roll, pitch, yaw)。
        is_degree (bool): 是否以角度表示输入。默认为 True

    Returns:
        Quaternion: 对应的旋转四元数
    """
    if is_degree:
        euler = degrees_to_radians(euler)

    roll, pitch, yaw = euler.x, euler.y, euler.z

    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy

    return Quaternion(w, x, y, z)


def quaternion_to_euler(q: Quaternion, is_degree: bool = True) -> Vector3:
    """
    将四元数转换为欧拉角（roll, pitch, yaw）。

    与 Unreal Engine 坐标系一致，旋转顺序 ZYX：
    - Roll (X)：绕 X 轴
    - Pitch (Y)：绕 Y 轴
    - Yaw (Z)：绕 Z 轴

    Args:
        q (Quaternion): 输入四元数
        is_degree (bool): 是否返回角度表示的欧拉角。默认单位为角度。

    Returns:
        Vector3: 欧拉角 (roll, pitch, yaw)
    """
    w, x, y, z = q.w, q.x, q.y, q.z

    # pitch (Y 轴)
    sinp = 2.0 * (w * y - z * x)
    pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)

    # yaw (Z 轴)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    # roll (X 轴)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    result = Vector3(roll, pitch, yaw)
    return radians_to_degrees(result) if is_degree else result


def calc_camera_look_at_rotation(pos: Vector3, target: Vector3) -> Quaternion:
    """
    计算相机从位置 `pos` 看向目标 `target` 时所需的旋转四元数。

    假设相机的局部前向为 +X 轴，世界上方向为 +Z 轴。

    Args:
        pos (Vector3): 相机位置。
        target (Vector3): 目标位置。

    Returns:
        Quaternion: 使相机看向目标所需的旋转。
    """
    world_up = Vector3(0.0, 0.0, 1.0)

    forward = normalize(target - pos)  # 相机前向（+X）
    right = cross(world_up, forward)

    # 处理 forward 与 world_up 平行（或反平行）的退化情况
    if length(right) < 1e-6:
        right = normalize(Vector3(0.0, 1.0, 0.0))  # 选取任意垂直方向
    else:
        right = normalize(right)

    up = cross(forward, right)

    # 构造旋转矩阵（列主序，右手坐标系）
    m00, m01, m02 = forward.x, right.x, up.x
    m10, m11, m12 = forward.y, right.y, up.y
    m20, m21, m22 = forward.z, right.z, up.z

    trace = m00 + m11 + m22

    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        w = 0.25 * s
        x = (m21 - m12) / s
        y = (m02 - m20) / s
        z = (m10 - m01) / s
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2.0
        w = (m21 - m12) / s
        x = 0.25 * s
        y = (m01 + m10) / s
        z = (m02 + m20) / s
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2.0
        w = (m02 - m20) / s
        x = (m01 + m10) / s
        y = 0.25 * s
        z = (m12 + m21) / s
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2.0
        w = (m10 - m01) / s
        x = (m02 + m20) / s
        y = (m12 + m21) / s
        z = 0.25 * s

    return Quaternion(w, x, y, z)


def distance(a: Vector3, b: Vector3) -> float:
    """
    计算两个向量的距离。

    Args:
        a (Vector3): 向量 a。
        b (Vector3): 向量 b。

    Returns:
        float: 两个向量的距离。
    """
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def decode_voxel(
    voxel_bytes: bytes, voxel_resolution: tuple[int, int, int]
) -> list[list[list[bool]]]:
    def decode_voxel_byte(byte: int):
        res = []
        mask = 1  # 掩码从 00000001 开始
        for _ in range(8):  # 每个字节有 8 位
            res.append((byte & mask) != 0)  # 按照位检查字节，是否为 1
            mask <<= 1  # 移动到下一个 bit
        return res  # 返回一个布尔值列表表示该字节的每一位

    num_voxel = (
        voxel_resolution[0] * voxel_resolution[1] * voxel_resolution[2]
    )  # 计算体素的总数量

    z_byte_num = num_voxel // 8
    if len(voxel_bytes) != z_byte_num:
        raise ValueError("data does not match the resolution!!!")

    total_res = []
    idx = 0

    for _ in range(voxel_resolution[0]):  # 遍历 x 方向
        y_res = []
        for _ in range(voxel_resolution[1]):  # 遍历 y 方向
            z_res = []
            for _ in range(voxel_resolution[2] // 8):  # 遍历 z 方向
                byte = voxel_bytes[idx]
                idx += 1

                z_res.extend(decode_voxel_byte(byte))
            y_res.append(z_res)
        total_res.append(y_res)

    return total_res
