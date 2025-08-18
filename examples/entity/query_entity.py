import tongsim as ts


def run_example():
    with ts.TongSim(
        grpc_endpoint="127.0.0.1:5056",
        legacy_grpc_endpoint="127.0.0.1:50052",
    ) as ue:
        # 加载地图（地图编号 0001，需确保资源存在）
        ue.open_level("Game_0001")

        # === 通过实体名称获取对象 ===
        # 注意：实体名称可能会随地图版本而变化，此处用于示范
        entity = ue.get_entity_by_name(ts.BaseObjectEntity, "BP_Book_08_C_1")
        print(f"Entity '{entity.id}' location: {entity.get_location()}")

        # 在三个不同位置生成三个相同的实体
        ue.spawn_entity(ts.BaseObjectEntity, "BP_Book_08", ts.Vector3(0, -300, 150))
        ue.spawn_entity(ts.BaseObjectEntity, "BP_Book_08", ts.Vector3(30, -300, 150))
        ue.spawn_entity(ts.BaseObjectEntity, "BP_Book_08", ts.Vector3(-30, -300, 150))

        # === 按 RDF 类型查询多个实体（如 book 类） ===
        # RDF 类型是一种语义标签，例如 "book"、"cup" 等
        entity_list = ue.get_entities_by_rdf_type(ts.BaseObjectEntity, "book")
        print(f"Found {len(entity_list)} book object(s):")
        for e in entity_list:
            print(f"  - {e.id}: location = {e.get_location()}")


if __name__ == "__main__":
    run_example()
