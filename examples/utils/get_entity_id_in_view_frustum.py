"""
示例名称:
视锥体剔除演示：查询一个视锥内的当前可见实体

说明:
    - 本示例使用的是基于 AABB（包围盒）进行的粗略视锥体剔除查询，
      属于高性能但低精度的检测方式，可能漏检小体积物体或产生误报。
    - 若需要更精确的可视物体检测（基于像素采样、遮挡判断等），
      请参考 CameraAbility 提供的 `fetch_visible_object_list_from_streaming` 方法。

功能:
    - 每秒获取一次当前视野内的实体 ID 列表；
    - 实体 ID 来自智能体头顶 120cm 高度处的摄像头方向；
    - 同时启动一个异步任务让智能体在场景中随机游走；
    - 支持按 `q` 键退出程序。
"""

import asyncio
import random

import tongsim as ts


async def keep_query_task(ue: ts.TongSim, agent: ts.AgentEntity):
    """
    持续进行视锥体查询，并输出结果实体 ID。
    """
    print("[INFO] 启动视锥体剔除任务...")

    while True:
        # 获取相机位置与旋转（从 agent 获取）
        pose = await agent.async_get_pose()
        camera_loc = pose.location + ts.Vector3(0, 0, 120)  # 摄像头高于角色头顶
        camera_rot = pose.rotation

        # 调用视锥体剔除查询
        # depthbuffer_width 和 depthbuffer_height 越大, 消耗性能越高，但对小物体的检测就越好
        # near_clip 和 far_clip 是 视锥的近平面和远平面， 单位为 cm
        subject_ids = (
            await ue.utils.async_get_subjects_in_view_frustum_with_aabb_culling(
                camera_loc=camera_loc,
                camera_rot=camera_rot,
                fov=90.0,
                view_width=1280.0,
                view_height=720.0,
                depthbuffer_width=128,
                depthbuffer_height=72,
                near_clip=0.0,
                far_clip=5000.0,
            )
        )

        print(f"\n[FRUSTUM] 当前可见实体数量: {len(subject_ids)}")
        for sid in subject_ids:
            print(f"  - {sid}")

        await asyncio.sleep(1.0)  # 每秒查询一次


async def random_walk_task(agent: ts.AgentEntity):
    """
    智能体随机游走任务：每次走向一个随机点。
    """
    print("[INFO] 启动智能体随机游走任务...")
    while True:
        target = ts.Vector3(
            random.uniform(-300, 300),
            random.uniform(-300, 300),
            100.0,
        )
        print(f"[MOVE] 智能体移动至随机目标点: {target}")
        await agent.async_do_action(ts.action.MoveToLocation(target))
        await asyncio.sleep(1.0)


def run_example():
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        # 加载关卡并生成智能体
        ue.open_level("Game_0001")
        agent = ue.spawn_agent(
            "SDBP_Aich_Robot", location=ts.Vector3(0.0, -300.0, 80.0)
        )
        ue.change_view_mode(ts.type.ViewModeType.THIRD_PERSON_VIEW)

        # 启动异步任务
        ue.context.async_task(keep_query_task(ue, agent), "frustum_task")
        ue.context.async_task(random_walk_task(agent), "walk_task")

        print("\n程序正在运行, 每秒刷新可视实体")
        print("输入 q 可退出程序\n")

        while True:
            cmd = input("输入 q 退出: ").strip().lower()
            if cmd == "q":
                print("程序已退出。")
                break


if __name__ == "__main__":
    run_example()
