import asyncio
import math
import time

import tongsim as ts
from tongsim import Vector3
from tongsim.math import euler_to_quaternion, quaternion_to_euler

# 退出事件，用于演示中中断任务
exit_event = asyncio.Event()


async def rotate_task(obj: ts.BaseObjectEntity, delta_rotate_degree: float = 2.0):
    """
    异步任务：让物体绕 Z 轴持续旋转。

    Args:
        obj (BaseObjectEntity): 要旋转的对象
        delta_rotate_degree (float): 每帧旋转角度（度），默认每帧旋转 2 度
    """
    delta_rad = math.radians(delta_rotate_degree)

    while not exit_event.is_set():
        # 获取当前欧拉角（单位：弧度）
        pose = await obj.async_get_pose()
        euler = quaternion_to_euler(pose.rotation, False)

        # 增加 Yaw（Z轴旋转）
        euler.z += delta_rad

        # 设置新的四元数旋转
        pose.rotation = euler_to_quaternion(euler, False)
        await obj.async_set_pose(pose)

        await asyncio.sleep(0.016)  # 模拟 60FPS


def run_example():
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        ue.open_level("Game_0001")

        print("[INFO] Spawning book at (0, 0, 100)")
        book = ue.spawn_entity(
            ts.BaseObjectEntity,
            blueprint="BP_Book_01",
            location=Vector3(0.0, -200.0, 100.0),
            scale=Vector3(3.0, 3.0, 3.0),
            is_simulating_physics=False,
        )

        # 启动异步旋转任务（在后台线程的 event loop 中运行）
        ue.context.async_task(
            rotate_task(book, delta_rotate_degree=3.0), "book_rotate_task"
        )

        print("[INFO] Book is now rotating... Press Ctrl+C to quit.")
        try:
            while True:
                time.sleep(1)  # 主线程保持运行
        except KeyboardInterrupt:
            print("[INFO] Exiting...")
            exit_event.set()


if __name__ == "__main__":
    run_example()
