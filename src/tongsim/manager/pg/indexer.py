class PGIndexer:
    """
    PGIndexer 提供全量 PG 数据结构中的 sid/cid -> 索引映射，
    便于快速定位 subject_pg / component_pg。
    """

    def __init__(self):
        self._subject_index: dict[str, int] = {}
        self._component_index: dict[tuple[str, str], int] = {}

    def clear(self):
        """重置索引状态"""
        self._subject_index.clear()
        self._component_index.clear()

    # ===== Subject 索引 =====

    def register_subject(self, sid: str, index: int):
        self._subject_index[sid] = index

    def has_subject(self, sid: str) -> bool:
        return sid in self._subject_index

    def get_subject_index(self, sid: str) -> int | None:
        return self._subject_index.get(sid)

    # ===== Component 索引 =====

    def register_component(self, sid: str, cid: str, index: int):
        self._component_index[(sid, cid)] = index

    def has_component(self, sid: str, cid: str) -> bool:
        return (sid, cid) in self._component_index

    def get_component_index(self, sid: str, cid: str) -> int | None:
        return self._component_index.get((sid, cid))
