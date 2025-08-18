"""
本示例演示:
如何启动 PG 流，并将 pose 组件中的位置和旋转信息写入 logs/pg-xxxx.json，
同时统计查询和写文件的耗时。
"""

import json
import os
import time
from datetime import datetime

import tongsim as ts

# 定义 PG 查询字段及别名映射, 可通过 pg_manager.get_pg_metainfo_schema() 查询
pg_metainfo = [
    {
        # 查询 pose 组件中的空间位置和旋转信息
        "component": "pose",
        "fields": ["location", "rotation"],  # 空间坐标与朝向四元数
    },
    {
        # 查询 object_state 中的物体类型字段
        "component": "object_state",
        "fields": ["object_type"],
        "as": {
            "object_type": "type",  # 重命名为更简洁的 type
        },
    },
    {
        # 查询 门、抽屉 等的位置
        "component": "door_state",
        "fields": ["transform", "b_closed"],
        "as": {
            "transform": "door_transform",  # 重命名
            "b_closed": "is_door_closed",
        },
    },
    {
        # 查询角色双手持物状态
        "component": "object_in_hand",
        "fields": ["left", "right", "two"],
        "as": {  # 重命名
            "left": "object_in_left_hand",  # 左手持物 ID
            "right": "object_in_right_hand",  # 右手持物 ID
            "two": "object_in_both_hands",  # 双手共同持物 ID
        },
    },
    {
        # 查询角色当前的能量值
        "component": "character_energy",
        "fields": ["energy"],
    },
    {
        # 查询角色当前的动画状态
        "component": "animation",
        "fields": [
            "full_body_type",  # 全身动作类型，例如 SLEEPING、SITTING
            "upper_body_type",  # 上半身动画状态
            "left_hand_state_type",  # 左手状态（举起、放下等）
            "right_hand_state_type",  # 右手状态
            "head_state_type",  # 头部朝向或动作状态
        ],
    },
]


def run_example():
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        # 启用 PG 模块调试日志（可选）
        # ts.set_log_level("pg", logging.DEBUG)

        # 加载关卡并生成一个 Agent
        ue.open_level("Game_0001")
        ue.spawn_agent("SDBP_Aich_Robot", ts.Vector3(0.0, -300.0, 80.0))

        # 打印当前 PG 系统支持的 metainfo 查询 schema（字段说明）
        print(
            f"PG metainfo schema:\n{json.dumps(ue.pg_manager.get_pg_metainfo_schema(), indent=2)}\n"
        )

        # 启动 PG 实时流，否则无法进行 PG 查询
        ue.pg_manager.start_pg_stream(pg_freq=30)  # 以 30Hz 频率接收 PG 数据

        print("Waiting for PG data...")
        time.sleep(2.0)  # 等待一段时间确保收到完整 PG 数据

        # 执行 PG 查询（pg_metainfo 应为一个已定义的查询结构）
        t0 = time.perf_counter()
        result = ue.pg_manager.query(pg_metainfo)
        t1 = time.perf_counter()

        # 构造日志输出路径
        log_dir = os.path.join(os.path.dirname(__file__), "../../", "logs")
        os.makedirs(log_dir, exist_ok=True)

        # 以当前时间生成唯一文件名
        filename = f"pg-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        filepath = os.path.join(log_dir, filename)

        # 写入查询结果（格式为 UTF-8 JSON）
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        t2 = time.perf_counter()

        # 打印性能统计信息与结果路径
        print(f"Query time: {(t1 - t0) * 1000:.2f} ms")
        print(f"Write to file time: {(t2 - t1) * 1000:.2f} ms")
        print(f"Query result written to: {filepath}")


if __name__ == "__main__":
    run_example()
