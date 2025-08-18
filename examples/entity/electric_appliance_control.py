"""
本示例演示:

- 如何获取并操作电器实体（如电视）。
- 如何通过遥控器控制电视的开关状态。
"""

import time

import tongsim as ts


def run_example():
    # 初始化 TongSim 实例，连接 gRPC 服务。
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        # 加载关卡。
        ue.open_level("Game_0103")

        # 获取电视实体（ElectricApplianceEntity）。
        tv = ue.get_entity_by_name(
            ts.ElectricApplianceEntity, "BP_Tray_Cup_Kitchen_C_1"
        )
        # 给电视通电，但尚未激活开关。
        tv.set_power_status(True)
        time.sleep(2.0)

        # 获取与电视同组的遥控器实体 ID (非比赛版本 TongSim 可通过 PG 或 接口直接查询)
        remote_controller = ue.entity_from_id(
            ts.InteractableEntity, "BP_RemoteController_01_C_1"
        )

        # 激活遥控器。
        remote_controller.set_active_state(True)


if __name__ == "__main__":
    run_example()
