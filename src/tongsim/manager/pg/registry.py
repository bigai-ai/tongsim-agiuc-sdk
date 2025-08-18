from typing import Final, TypedDict


class ComponentSchema(TypedDict):
    fields: list[str]
    allow_multiple: bool  # 是否允许同类型组件重复出现


# 定义组件类型到其字段列表的映射(需要和 proto 的定义严格对齐!)
# 该表是全量不可修改，在 query 和 schema 都会被使用
PG_COMPONENT_REGISTRY: Final[dict[str, ComponentSchema]] = {
    "pose": {
        "fields": ["location", "rotation"],
        "allow_multiple": False,
    },
    "scale": {
        "fields": ["x", "y", "z"],
        "allow_multiple": False,
    },
    "aabb": {
        "fields": ["min_vertex", "max_vertex"],
        "allow_multiple": False,
    },
    "ue_collision_vertexes": {
        "fields": ["vertexes"],
        "allow_multiple": False,
    },
    "character_energy": {
        "fields": ["energy", "max_walk_distance"],
        "allow_multiple": False,
    },
    "food_energy": {
        "fields": [
            "edible_category",
            "anti_hungry",
            "anti_thirsty",
            "cubage",
            "residue_volume",
        ],
        "allow_multiple": False,
    },
    "capsule": {
        "fields": ["radius", "half_height"],
        "allow_multiple": False,
    },
    "object_in_hand": {
        "fields": ["left", "right", "two"],
        "allow_multiple": False,
    },
    "object_state": {  # 此组件下有大量其他fileds，目前没有全部配置
        "fields": [
            "b_state_active",
            "group_id",
            "object_type",
            "color",
            "shape",
            "wearing",
            "wearingby",
            "channel",
            "b_lock",
            "segment_id",
        ],
        "allow_multiple": False,
    },
    "container_state": {
        "fields": [
            "box",
            "transform",
            "residue_volume",
            "place_objects",
            "door_components",
        ],
        "allow_multiple": True,
    },
    "door_state": {
        "fields": [
            "b_impassable_door",
            "transform",
            "max_open_angular_or_distances",
            "open_angular_or_distance",
            "b_closed",
            "door_type",
        ],
        "allow_multiple": True,
    },
    "common_attribute": {
        "fields": [
            "sleepy",
            "boredom",
            "asset",
            "common_struct",
            "relation_struct",
        ],
        "allow_multiple": False,
    },
    "camera_param": {
        "fields": ["fov", "width", "height", "luminance"],
        "allow_multiple": False,
    },
    "character_attribute": {
        "fields": ["sleepy", "boredom", "temperature"],
        "allow_multiple": False,
    },
    "emotion_state": {
        "fields": ["emotion"],
        "allow_multiple": False,
    },
    "view_info": {
        "fields": ["camera_pose", "camera_param"],
        "allow_multiple": False,
    },
    "animation": {
        "fields": [
            "full_body_type",
            "upper_body_type",
            "left_hand_state_type",
            "right_hand_state_type",
            "head_state_type",
            "current_command_ids",
            "current_speed",
            "bone_list",
        ],
        "allow_multiple": False,
    },
    # 如有新组件请在此处附加，同时维护字段名类型对齐
}
