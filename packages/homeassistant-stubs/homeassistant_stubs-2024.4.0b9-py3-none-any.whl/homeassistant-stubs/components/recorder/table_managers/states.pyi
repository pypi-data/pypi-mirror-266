from ..db_schema import States as States
from _typeshed import Incomplete

class StatesManager:
    _pending: Incomplete
    _last_committed_id: Incomplete
    _last_reported: Incomplete
    def __init__(self) -> None: ...
    def pop_pending(self, entity_id: str) -> States | None: ...
    def pop_committed(self, entity_id: str) -> int | None: ...
    def add_pending(self, entity_id: str, state: States) -> None: ...
    def update_pending_last_reported(self, state_id: int, last_reported_timestamp: float) -> None: ...
    def get_pending_last_reported_timestamp(self) -> dict[int, float]: ...
    def post_commit_pending(self) -> None: ...
    def reset(self) -> None: ...
    def evict_purged_state_ids(self, purged_state_ids: set[int]) -> None: ...
    def evict_purged_entity_ids(self, purged_entity_ids: set[str]) -> None: ...
