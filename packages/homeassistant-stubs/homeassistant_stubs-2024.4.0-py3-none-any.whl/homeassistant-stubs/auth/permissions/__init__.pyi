from .merge import merge_policies as merge_policies
from .models import PermissionLookup as PermissionLookup
from .types import PolicyType as PolicyType
from _typeshed import Incomplete
from collections.abc import Callable
from typing import Any

__all__ = ['POLICY_SCHEMA', 'merge_policies', 'PermissionLookup', 'PolicyType', 'AbstractPermissions', 'PolicyPermissions', 'OwnerPermissions']

POLICY_SCHEMA: Incomplete

class AbstractPermissions:
    _cached_entity_func: Callable[[str, str], bool] | None
    def _entity_func(self) -> Callable[[str, str], bool]: ...
    def access_all_entities(self, key: str) -> bool: ...
    def check_entity(self, entity_id: str, key: str) -> bool: ...

class PolicyPermissions(AbstractPermissions):
    _policy: Incomplete
    _perm_lookup: Incomplete
    def __init__(self, policy: PolicyType, perm_lookup: PermissionLookup) -> None: ...
    def access_all_entities(self, key: str) -> bool: ...
    def _entity_func(self) -> Callable[[str, str], bool]: ...
    def __eq__(self, other: Any) -> bool: ...

class _OwnerPermissions(AbstractPermissions):
    def access_all_entities(self, key: str) -> bool: ...
    def _entity_func(self) -> Callable[[str, str], bool]: ...

OwnerPermissions: Incomplete
