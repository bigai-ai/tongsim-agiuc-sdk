"""
示例: 不断在空中随机位置生成书本实体，并在随机时间后销毁。
可用于测试实体创建与销毁接口，以及空间位置控制。

依赖:
    - 确保存在名为 "BP_Book_01" 的资产


按 Ctrl+C 可手动终止示例。
"""

import random
import time

import tongsim as ts


def run_example():
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        ue.open_level("Game_0001")  # 加载关卡

        print("[INFO] 开始循环生成并销毁书本实体... 按 Ctrl+C 中断。")

        try:
            while True:
                # 随机生成位置
                x = random.uniform(-200, 0)
                y = random.uniform(-300, 100)
                z = random.uniform(100, 200)
                location = ts.Vector3(x, y, z)

                # 创建书本实体
                book = ue.spawn_entity(ts.BaseObjectEntity, "BP_Book_01", location)
                print(f"[INFO] Spawned book at {location}, ID: {book.id}")

                # 等待一段随机时间后销毁（1~2秒）
                wait_time = random.uniform(1.0, 2.0)
                time.sleep(wait_time)

                ue.destroy_entity(book.id)
                print(f"[INFO] Destroyed book: {book.id} after {wait_time:.2f} seconds")

        except KeyboardInterrupt:
            print("[INFO] 手动终止示例。")


if __name__ == "__main__":
    run_example()
