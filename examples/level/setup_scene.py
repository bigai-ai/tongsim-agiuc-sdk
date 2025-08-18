"""
示例: 依次切换多个关卡，创建智能体与摄像头，并启动 PG 与图像流。验证异步任务的释放。

功能演示:
- 加载多个地图（Level）
- 启动图像流和 PG 数据流采集

注意:
- 每次切换地图后 sleep 一段时间，保证数据流稳定

"""

import time

import tongsim as ts


def setup_scene(ue: ts.TongSim, level_name: str):
    """
    初始化关卡场景，创建智能体和摄像头，并绑定与启动数据流。

    参数:
        ue (ts.TongSim): TongSim 实例。
        level_name (str): 要加载的关卡名称。
    """
    # 加载指定地图
    ue.open_level(level_name)

    # 在原点生成智能体
    agent = ue.spawn_agent("SDBP_Aich_Robot", location=ts.Vector3(0.0, 0.0, 0.0))

    # 在智能体上生成摄像头
    camera = ue.spawn_camera(
        f"{level_name}_camera_1",
        loc=ts.Vector3(0.0, 0.0, 80.0),
        quat=ts.Quaternion(),
    )
    camera.attach_to_target_socket(agent.id, socket_name="MidCameraSocket")

    # 启用图像数据流（RGB）
    camera.start_imagedata_streaming(True)

    # 启动 PG 数据流（30Hz）
    ue.pg_manager.start_pg_stream(pg_freq=30)

    # 输出 当前的 task 列表
    # ue.context.loop.log_task_list()


def run_example():
    # 启用 logger:
    ts.initialize_logger()

    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        for level_name in [
            "Game_0000",
            "Game_0001",
            "Game_0002",
            "Game_0003",
        ]:
            setup_scene(ue, level_name)
            time.sleep(2.0)  # 等待数据流稳定


if __name__ == "__main__":
    run_example()
