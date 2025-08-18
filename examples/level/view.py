"""
本示例演示: 如何通过 SDK 切换相机视角（ViewModeType 全枚举）。

可动态切换以下模式（需根据运行版本支持情况选择）。
"""

import tongsim as ts
from tongsim.type import ViewModeType


def run_example():
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        # 加载关卡并放置一个 Agent（用于第一/第三/面对面视角）
        ue.open_level("Game_0001")
        ue.spawn_agent("SDBP_Aich_Robot", location=ts.Vector3(0.0, -300.0, 80.0))

        print("\n=== 🎥 摄像机视角切换演示(AGIUC 的 机器人角色仅支持 1 3 4 5) ===")
        print("请输入编号切换视角模式:")
        print("  1 - 第一人称视角         (First-Person View)")
        print("  2 - 面对面视角           (Face-to-Face View, 仅 TongLoop 支持)")
        print("  3 - 第三人称视角         (Third-Person View)")
        print("  4 - 自由控制视角         (Manual Control View, WASD/空格/Ctrl)")
        print("  5 - 静态监控视角         (Surveillance View)")
        print("  q - 退出程序")
        print()

        while True:
            cmd = input("请输入指令: ").strip().lower()

            if cmd == "1":
                success = ue.change_view_mode(ViewModeType.FIRST_PERSON_VIEW)
                print(f"切换到【第一人称视角】: {'✅ 成功' if success else '❌ 失败'}")

            elif cmd == "2":
                success = ue.change_view_mode(ViewModeType.FACE_TO_FACE_VIEW)
                print(f"切换到【面对面视角】: {'✅ 成功' if success else '❌ 失败'}")

            elif cmd == "3":
                success = ue.change_view_mode(ViewModeType.THIRD_PERSON_VIEW)
                print(f"切换到【第三人称视角】: {'✅ 成功' if success else '❌ 失败'}")

            elif cmd == "4":
                success = ue.change_view_mode(ViewModeType.MANUAL_CONTROL_VIEW)
                print(
                    f"切换到【自由控制视角】(WASD 控制): {'✅ 成功' if success else '❌ 失败'}"
                )

            elif cmd == "5":
                success = ue.change_view_mode(ViewModeType.SURVEILLANCE_VIEW)
                print(f"切换到【静态监控视角】: {'✅ 成功' if success else '❌ 失败'}")

            elif cmd == "q":
                print("👋 程序已退出。")
                break

            else:
                print("⚠️ 无效输入, 请输入 1-5 或 q。")


if __name__ == "__main__":
    run_example()
