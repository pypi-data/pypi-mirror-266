import asyncio
import voluptuous as vol
from . import service as service, translation as translation
from .entity import Entity as Entity
from .entity_registry import EntityRegistry as EntityRegistry, RegistryEntryDisabler as RegistryEntryDisabler, RegistryEntryHider as RegistryEntryHider
from .event import async_call_later as async_call_later, async_track_time_interval as async_track_time_interval
from .issue_registry import IssueSeverity as IssueSeverity, async_create_issue as async_create_issue
from .typing import ConfigType as ConfigType, DiscoveryInfoType as DiscoveryInfoType, UNDEFINED as UNDEFINED
from _typeshed import Incomplete
from collections.abc import Awaitable, Callable as Callable, Coroutine, Iterable
from contextvars import ContextVar
from datetime import datetime, timedelta
from homeassistant import config_entries as config_entries
from homeassistant.const import ATTR_RESTORED as ATTR_RESTORED, DEVICE_DEFAULT_NAME as DEVICE_DEFAULT_NAME, EVENT_HOMEASSISTANT_STARTED as EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CALLBACK_TYPE as CALLBACK_TYPE, CoreState as CoreState, HassJob as HassJob, HomeAssistant as HomeAssistant, ServiceCall as ServiceCall, SupportsResponse as SupportsResponse, callback as callback, split_entity_id as split_entity_id, valid_entity_id as valid_entity_id
from homeassistant.exceptions import HomeAssistantError as HomeAssistantError, PlatformNotReady as PlatformNotReady
from homeassistant.generated import languages as languages
from homeassistant.setup import SetupPhases as SetupPhases, async_start_setup as async_start_setup
from homeassistant.util.async_ import create_eager_task as create_eager_task
from logging import Logger
from typing import Any, Protocol

SLOW_SETUP_WARNING: int
SLOW_SETUP_MAX_WAIT: int
SLOW_ADD_ENTITY_MAX_WAIT: int
SLOW_ADD_MIN_TIMEOUT: int
PLATFORM_NOT_READY_RETRIES: int
DATA_ENTITY_PLATFORM: str
DATA_DOMAIN_ENTITIES: str
DATA_DOMAIN_PLATFORM_ENTITIES: str
PLATFORM_NOT_READY_BASE_WAIT_TIME: int
_LOGGER: Incomplete

class AddEntitiesCallback(Protocol):
    def __call__(self, new_entities: Iterable[Entity], update_before_add: bool = False) -> None: ...

class EntityPlatformModule(Protocol):
    async def async_setup_platform(self, hass: HomeAssistant, config: ConfigType, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None) -> None: ...
    def setup_platform(self, hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None) -> None: ...
    async def async_setup_entry(self, hass: HomeAssistant, entry: config_entries.ConfigEntry, async_add_entities: AddEntitiesCallback) -> None: ...

class EntityPlatform:
    hass: Incomplete
    logger: Incomplete
    domain: Incomplete
    platform_name: Incomplete
    platform: Incomplete
    scan_interval: Incomplete
    entity_namespace: Incomplete
    config_entry: Incomplete
    entities: Incomplete
    component_translations: Incomplete
    platform_translations: Incomplete
    object_id_component_translations: Incomplete
    object_id_platform_translations: Incomplete
    _tasks: Incomplete
    _setup_complete: bool
    _async_unsub_polling: Incomplete
    _async_cancel_retry_setup: Incomplete
    _process_updates: Incomplete
    parallel_updates: Incomplete
    _update_in_sequence: bool
    parallel_updates_created: Incomplete
    domain_entities: Incomplete
    domain_platform_entities: Incomplete
    def __init__(self, *, hass: HomeAssistant, logger: Logger, domain: str, platform_name: str, platform: EntityPlatformModule | None, scan_interval: timedelta, entity_namespace: str | None) -> None: ...
    def __repr__(self) -> str: ...
    def _get_parallel_updates_semaphore(self, entity_has_sync_update: bool) -> asyncio.Semaphore | None: ...
    async def async_setup(self, platform_config: ConfigType, discovery_info: DiscoveryInfoType | None = None) -> None: ...
    def async_shutdown(self) -> None: ...
    def async_cancel_retry_setup(self) -> None: ...
    async def async_setup_entry(self, config_entry: config_entries.ConfigEntry) -> bool: ...
    async def _async_setup_platform(self, async_create_setup_awaitable: Callable[[], Awaitable[None]], tries: int = 0) -> bool: ...
    async def _async_get_translations(self, language: str, category: str, integration: str) -> dict[str, str]: ...
    async def async_load_translations(self) -> None: ...
    def _schedule_add_entities(self, new_entities: Iterable[Entity], update_before_add: bool = False) -> None: ...
    def _async_schedule_add_entities(self, new_entities: Iterable[Entity], update_before_add: bool = False) -> None: ...
    def _async_schedule_add_entities_for_entry(self, new_entities: Iterable[Entity], update_before_add: bool = False) -> None: ...
    def add_entities(self, new_entities: Iterable[Entity], update_before_add: bool = False) -> None: ...
    async def _async_add_and_update_entities(self, coros: list[Coroutine[Any, Any, None]], entities: list[Entity], timeout: float) -> None: ...
    async def _async_add_entities(self, coros: list[Coroutine[Any, Any, None]], entities: list[Entity], timeout: float) -> None: ...
    async def async_add_entities(self, new_entities: Iterable[Entity], update_before_add: bool = False) -> None: ...
    def _async_handle_interval_callback(self, now: datetime) -> None: ...
    def _entity_id_already_exists(self, entity_id: str) -> tuple[bool, bool]: ...
    async def _async_add_entity(self, entity: Entity, update_before_add: bool, entity_registry: EntityRegistry) -> None: ...
    async def async_reset(self) -> None: ...
    def async_unsub_polling(self) -> None: ...
    def async_prepare(self) -> None: ...
    async def async_destroy(self) -> None: ...
    async def async_remove_entity(self, entity_id: str) -> None: ...
    async def async_extract_from_service(self, service_call: ServiceCall, expand_group: bool = True) -> list[Entity]: ...
    def async_register_entity_service(self, name: str, schema: dict[str | vol.Marker, Any] | vol.Schema, func: str | Callable[..., Any], required_features: Iterable[int] | None = None, supports_response: SupportsResponse = ...) -> None: ...
    async def _update_entity_states(self, now: datetime) -> None: ...

current_platform: ContextVar[EntityPlatform | None]

def async_get_current_platform() -> EntityPlatform: ...
def async_get_platforms(hass: HomeAssistant, integration_name: str) -> list[EntityPlatform]: ...
