import tongsim as ts


def run_example():
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        # 加载关卡
        ue.open_level("Game_0001")

        # 生成一个实体（书本），位置在 Z=100，高于地面
        book = ue.spawn_entity(
            ts.BaseObjectEntity,
            blueprint="BP_Book_01",
            location=ts.Vector3(0.0, -300.0, 100.0),
            quat=ts.math.euler_to_quaternion(ts.Vector3(0.0, 0.0, -90.0)),
            is_simulating_physics=False,
        )
        print(f"Spawned book entity: id={book.id}")

        # 获取初始状态
        initial_transform = book.get_transform()
        print(f"Initial transform: {initial_transform}")

        # 获取并打印初始 AABB
        print("\n=== 初始状态 AABB ===")
        relative_aabb = book.get_relative_aabb()
        world_aabb = book.get_world_aabb()
        print(f"[Relative AABB] min={relative_aabb.min}, max={relative_aabb.max}")
        print(f"[World AABB]    min={world_aabb.min}, max={world_aabb.max}")

        # 调整 scale 为 2倍
        new_scale = ts.Vector3(2.0, 2.0, 2.0)
        print(f"\n=== 调整 Scale 为 {new_scale} ===")
        book.set_scale(new_scale)

        # 获取并打印调整后的 AABB
        print("\n=== 调整后状态 AABB ===")
        updated_relative_aabb = book.get_relative_aabb()
        updated_world_aabb = book.get_world_aabb()
        print(
            f"[Relative AABB] min={updated_relative_aabb.min}, max={updated_relative_aabb.max}"
        )
        print(
            f"[World AABB]    min={updated_world_aabb.min}, max={updated_world_aabb.max}"
        )


if __name__ == "__main__":
    run_example()
