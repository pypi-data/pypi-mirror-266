from .domain_data import DomainData as DomainData
from .entry_data import RuntimeEntryData as RuntimeEntryData
from .enum_mapper import EsphomeEnumMapper as EsphomeEnumMapper
from _typeshed import Incomplete
from aioesphomeapi import EntityCategory as EsphomeEntityCategory, EntityInfo, EntityState
from collections.abc import Awaitable, Callable as Callable, Coroutine
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import EntityCategory as EntityCategory
from homeassistant.core import HomeAssistant as HomeAssistant, callback as callback
from homeassistant.exceptions import HomeAssistantError as HomeAssistantError
from homeassistant.helpers import entity_platform as entity_platform
from homeassistant.helpers.device_registry import DeviceInfo as DeviceInfo
from homeassistant.helpers.entity import Entity as Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback as AddEntitiesCallback
from typing import Any, Concatenate, Generic, ParamSpec, TypeVar

_R = TypeVar('_R')
_P = ParamSpec('_P')
_InfoT = TypeVar('_InfoT', bound=EntityInfo)
_EntityT = TypeVar('_EntityT', bound='EsphomeEntity[Any,Any]')
_StateT = TypeVar('_StateT', bound=EntityState)

def async_static_info_updated(hass: HomeAssistant, entry_data: RuntimeEntryData, platform: entity_platform.EntityPlatform, async_add_entities: AddEntitiesCallback, info_type: type[_InfoT], entity_type: type[_EntityT], state_type: type[_StateT], infos: list[EntityInfo]) -> None: ...
async def platform_async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback, *, info_type: type[_InfoT], entity_type: type[_EntityT], state_type: type[_StateT]) -> None: ...
def esphome_state_property(func: Callable[[_EntityT], _R]) -> Callable[[_EntityT], _R | None]: ...
def convert_api_error_ha_error(func: Callable[Concatenate[_EntityT, _P], Awaitable[None]]) -> Callable[Concatenate[_EntityT, _P], Coroutine[Any, Any, None]]: ...

ICON_SCHEMA: Incomplete
ENTITY_CATEGORIES: EsphomeEnumMapper[EsphomeEntityCategory, EntityCategory | None]

class EsphomeEntity(Entity, Generic[_InfoT, _StateT]):
    _attr_should_poll: bool
    _static_info: _InfoT
    _state: _StateT
    _has_state: bool
    _entry_data: Incomplete
    _key: Incomplete
    _state_type: Incomplete
    _device_info: Incomplete
    _attr_device_info: Incomplete
    _attr_has_entity_name: bool
    entity_id: Incomplete
    def __init__(self, entry_data: RuntimeEntryData, domain: str, entity_info: EntityInfo, state_type: type[_StateT]) -> None: ...
    async def async_added_to_hass(self) -> None: ...
    _attr_unique_id: Incomplete
    _attr_entity_registry_enabled_default: Incomplete
    _attr_name: Incomplete
    _attr_entity_category: Incomplete
    _attr_icon: Incomplete
    def _on_static_info_update(self, static_info: EntityInfo) -> None: ...
    def _update_state_from_entry_data(self) -> None: ...
    def _on_state_update(self) -> None: ...
    _api_version: Incomplete
    _client: Incomplete
    def _on_entry_data_changed(self) -> None: ...
    def _on_device_update(self) -> None: ...
    @property
    def available(self) -> bool: ...

class EsphomeAssistEntity(Entity):
    _attr_has_entity_name: bool
    _attr_should_poll: bool
    _entry_data: Incomplete
    _device_info: Incomplete
    _attr_unique_id: Incomplete
    _attr_device_info: Incomplete
    def __init__(self, entry_data: RuntimeEntryData) -> None: ...
    async def async_added_to_hass(self) -> None: ...
