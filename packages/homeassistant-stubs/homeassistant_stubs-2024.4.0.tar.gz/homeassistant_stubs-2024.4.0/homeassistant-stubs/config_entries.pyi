import asyncio
from . import data_entry_flow as data_entry_flow, loader as loader
from .components import persistent_notification as persistent_notification
from .components.bluetooth import BluetoothServiceInfoBleak as BluetoothServiceInfoBleak
from .components.dhcp import DhcpServiceInfo as DhcpServiceInfo
from .components.hassio import HassioServiceInfo as HassioServiceInfo
from .components.ssdp import SsdpServiceInfo as SsdpServiceInfo
from .components.usb import UsbServiceInfo as UsbServiceInfo
from .components.zeroconf import ZeroconfServiceInfo as ZeroconfServiceInfo
from .const import EVENT_HOMEASSISTANT_STARTED as EVENT_HOMEASSISTANT_STARTED, EVENT_HOMEASSISTANT_STOP as EVENT_HOMEASSISTANT_STOP, Platform as Platform
from .core import CALLBACK_TYPE as CALLBACK_TYPE, CoreState as CoreState, Event as Event, HassJob as HassJob, HassJobType as HassJobType, HomeAssistant as HomeAssistant, callback as callback
from .data_entry_flow import FLOW_NOT_COMPLETE_STEPS as FLOW_NOT_COMPLETE_STEPS, FlowResult as FlowResult
from .exceptions import ConfigEntryAuthFailed as ConfigEntryAuthFailed, ConfigEntryError as ConfigEntryError, ConfigEntryNotReady as ConfigEntryNotReady, HomeAssistantError as HomeAssistantError
from .helpers import device_registry as device_registry, entity_registry as entity_registry, storage as storage
from .helpers.debounce import Debouncer as Debouncer
from .helpers.dispatcher import SignalType as SignalType, async_dispatcher_send as async_dispatcher_send
from .helpers.event import RANDOM_MICROSECOND_MAX as RANDOM_MICROSECOND_MAX, RANDOM_MICROSECOND_MIN as RANDOM_MICROSECOND_MIN, async_call_later as async_call_later
from .helpers.frame import report as report
from .helpers.json import json_bytes as json_bytes, json_fragment as json_fragment
from .helpers.service_info.mqtt import MqttServiceInfo as MqttServiceInfo
from .helpers.typing import ConfigType as ConfigType, DiscoveryInfoType as DiscoveryInfoType, UNDEFINED as UNDEFINED, UndefinedType as UndefinedType
from .loader import async_suggest_report_issue as async_suggest_report_issue
from .setup import DATA_SETUP_DONE as DATA_SETUP_DONE, SetupPhases as SetupPhases, async_pause_setup as async_pause_setup, async_process_deps_reqs as async_process_deps_reqs, async_setup_component as async_setup_component, async_start_setup as async_start_setup
from .util.async_ import create_eager_task as create_eager_task
from .util.decorator import Registry as Registry
from _typeshed import Incomplete
from collections import UserDict
from collections.abc import Callable, Coroutine, Generator, Iterable, Mapping, ValuesView
from contextvars import ContextVar
from enum import Enum, StrEnum
from functools import cached_property as cached_property
from types import MappingProxyType
from typing import Any, Self, TypeVar

_LOGGER: Incomplete
SOURCE_BLUETOOTH: str
SOURCE_DHCP: str
SOURCE_DISCOVERY: str
SOURCE_HARDWARE: str
SOURCE_HASSIO: str
SOURCE_HOMEKIT: str
SOURCE_IMPORT: str
SOURCE_INTEGRATION_DISCOVERY: str
SOURCE_MQTT: str
SOURCE_SSDP: str
SOURCE_SYSTEM: str
SOURCE_USB: str
SOURCE_USER: str
SOURCE_ZEROCONF: str
SOURCE_IGNORE: str
SOURCE_UNIGNORE: str
SOURCE_REAUTH: str
SOURCE_RECONFIGURE: str
HANDLERS: Registry[str, type[ConfigFlow]]
STORAGE_KEY: str
STORAGE_VERSION: int
PATH_CONFIG: str
SAVE_DELAY: int
DISCOVERY_COOLDOWN: int
_R = TypeVar('_R')

class ConfigEntryState(Enum):
    LOADED: Incomplete
    SETUP_ERROR: Incomplete
    MIGRATION_ERROR: Incomplete
    SETUP_RETRY: Incomplete
    NOT_LOADED: Incomplete
    FAILED_UNLOAD: Incomplete
    SETUP_IN_PROGRESS: Incomplete
    _recoverable: bool
    def __new__(cls, value: str, recoverable: bool) -> Self: ...
    @property
    def recoverable(self) -> bool: ...

DEFAULT_DISCOVERY_UNIQUE_ID: str
DISCOVERY_NOTIFICATION_ID: str
DISCOVERY_SOURCES: Incomplete
RECONFIGURE_NOTIFICATION_ID: str
EVENT_FLOW_DISCOVERED: str
SIGNAL_CONFIG_ENTRY_CHANGED: Incomplete
NO_RESET_TRIES_STATES: Incomplete

class ConfigEntryChange(StrEnum):
    ADDED: str
    REMOVED: str
    UPDATED: str

class ConfigEntryDisabler(StrEnum):
    USER: str

DISABLED_USER: Incomplete
RELOAD_AFTER_UPDATE_DELAY: int
CONN_CLASS_CLOUD_PUSH: str
CONN_CLASS_CLOUD_POLL: str
CONN_CLASS_LOCAL_PUSH: str
CONN_CLASS_LOCAL_POLL: str
CONN_CLASS_ASSUMED: str
CONN_CLASS_UNKNOWN: str

class ConfigError(HomeAssistantError): ...
class UnknownEntry(ConfigError): ...
class OperationNotAllowed(ConfigError): ...

UpdateListenerType: Incomplete
FROZEN_CONFIG_ENTRY_ATTRS: Incomplete
UPDATE_ENTRY_CONFIG_ENTRY_ATTRS: Incomplete

class ConfigFlowResult(FlowResult, total=False):
    minor_version: int
    version: int

class ConfigEntry:
    entry_id: str
    domain: str
    title: str
    data: MappingProxyType[str, Any]
    options: MappingProxyType[str, Any]
    unique_id: str | None
    state: ConfigEntryState
    reason: str | None
    pref_disable_new_entities: bool
    pref_disable_polling: bool
    version: int
    minor_version: int
    source: Incomplete
    disabled_by: Incomplete
    supports_unload: Incomplete
    supports_remove_device: Incomplete
    _supports_options: Incomplete
    _supports_reconfigure: Incomplete
    update_listeners: Incomplete
    _async_cancel_retry_setup: Incomplete
    _on_unload: Incomplete
    reload_lock: Incomplete
    _reauth_lock: Incomplete
    _reconfigure_lock: Incomplete
    _tasks: Incomplete
    _background_tasks: Incomplete
    _integration_for_domain: Incomplete
    _tries: int
    def __init__(self, *, version: int, minor_version: int, domain: str, title: str, data: Mapping[str, Any], source: str, pref_disable_new_entities: bool | None = None, pref_disable_polling: bool | None = None, options: Mapping[str, Any] | None = None, unique_id: str | None = None, entry_id: str | None = None, state: ConfigEntryState = ..., disabled_by: ConfigEntryDisabler | None = None) -> None: ...
    def __repr__(self) -> str: ...
    def __setattr__(self, key: str, value: Any) -> None: ...
    @property
    def supports_options(self) -> bool: ...
    @property
    def supports_reconfigure(self) -> bool: ...
    def clear_cache(self) -> None: ...
    @cached_property
    def as_json_fragment(self) -> json_fragment: ...
    async def async_setup(self, hass: HomeAssistant, *, integration: loader.Integration | None = None) -> None: ...
    def _async_setup_again(self, hass: HomeAssistant, *_: Any) -> None: ...
    def async_shutdown(self) -> None: ...
    def async_cancel_retry_setup(self) -> None: ...
    async def async_unload(self, hass: HomeAssistant, *, integration: loader.Integration | None = None) -> bool: ...
    async def async_remove(self, hass: HomeAssistant) -> None: ...
    def _async_set_state(self, hass: HomeAssistant, state: ConfigEntryState, reason: str | None) -> None: ...
    async def async_migrate(self, hass: HomeAssistant) -> bool: ...
    def add_update_listener(self, listener: UpdateListenerType) -> CALLBACK_TYPE: ...
    def as_dict(self) -> dict[str, Any]: ...
    def async_on_unload(self, func: Callable[[], Coroutine[Any, Any, None] | None]) -> None: ...
    async def _async_process_on_unload(self, hass: HomeAssistant) -> None: ...
    def async_start_reauth(self, hass: HomeAssistant, context: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> None: ...
    async def _async_init_reauth(self, hass: HomeAssistant, context: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> None: ...
    def async_start_reconfigure(self, hass: HomeAssistant, context: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> None: ...
    async def _async_init_reconfigure(self, hass: HomeAssistant, context: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> None: ...
    def async_get_active_flows(self, hass: HomeAssistant, sources: set[str]) -> Generator[ConfigFlowResult, None, None]: ...
    def async_create_task(self, hass: HomeAssistant, target: Coroutine[Any, Any, _R], name: str | None = None, eager_start: bool = False) -> asyncio.Task[_R]: ...
    def async_create_background_task(self, hass: HomeAssistant, target: Coroutine[Any, Any, _R], name: str, eager_start: bool = False) -> asyncio.Task[_R]: ...

current_entry: ContextVar[ConfigEntry | None]

class FlowCancelledError(Exception): ...

class ConfigEntriesFlowManager(data_entry_flow.FlowManager[ConfigFlowResult, str]):
    _flow_result = ConfigFlowResult
    config_entries: Incomplete
    _hass_config: Incomplete
    _pending_import_flows: Incomplete
    _initialize_futures: Incomplete
    _discovery_debouncer: Incomplete
    def __init__(self, hass: HomeAssistant, config_entries: ConfigEntries, hass_config: ConfigType) -> None: ...
    async def async_wait_import_flow_initialized(self, handler: str) -> None: ...
    def _async_has_other_discovery_flows(self, flow_id: str) -> bool: ...
    async def async_init(self, handler: str, *, context: dict[str, Any] | None = None, data: Any = None) -> ConfigFlowResult: ...
    async def _async_init(self, flow_id: str, handler: str, context: dict, data: Any) -> tuple[ConfigFlow, ConfigFlowResult]: ...
    def async_shutdown(self) -> None: ...
    async def async_finish_flow(self, flow: data_entry_flow.FlowHandler[ConfigFlowResult, str], result: ConfigFlowResult) -> ConfigFlowResult: ...
    async def async_create_flow(self, handler_key: str, *, context: dict | None = None, data: Any = None) -> ConfigFlow: ...
    async def async_post_init(self, flow: data_entry_flow.FlowHandler[ConfigFlowResult, str], result: ConfigFlowResult) -> None: ...
    def _async_discovery(self) -> None: ...

class ConfigEntryItems(UserDict[str, ConfigEntry]):
    _hass: Incomplete
    _domain_index: Incomplete
    _domain_unique_id_index: Incomplete
    def __init__(self, hass: HomeAssistant) -> None: ...
    def values(self) -> ValuesView[ConfigEntry]: ...
    def __setitem__(self, entry_id: str, entry: ConfigEntry) -> None: ...
    def _index_entry(self, entry: ConfigEntry) -> None: ...
    def _unindex_entry(self, entry_id: str) -> None: ...
    def __delitem__(self, entry_id: str) -> None: ...
    def update_unique_id(self, entry: ConfigEntry, new_unique_id: str | None) -> None: ...
    def get_entries_for_domain(self, domain: str) -> list[ConfigEntry]: ...
    def get_entry_by_domain_and_unique_id(self, domain: str, unique_id: str) -> ConfigEntry | None: ...

class ConfigEntries:
    hass: Incomplete
    flow: Incomplete
    options: Incomplete
    _hass_config: Incomplete
    _entries: Incomplete
    _store: Incomplete
    def __init__(self, hass: HomeAssistant, hass_config: ConfigType) -> None: ...
    def async_domains(self, include_ignore: bool = False, include_disabled: bool = False) -> list[str]: ...
    def async_get_entry(self, entry_id: str) -> ConfigEntry | None: ...
    def async_entry_ids(self) -> list[str]: ...
    def async_entries(self, domain: str | None = None, include_ignore: bool = True, include_disabled: bool = True) -> list[ConfigEntry]: ...
    def async_entry_for_domain_unique_id(self, domain: str, unique_id: str) -> ConfigEntry | None: ...
    async def async_add(self, entry: ConfigEntry) -> None: ...
    async def async_remove(self, entry_id: str) -> dict[str, Any]: ...
    def _async_shutdown(self, event: Event) -> None: ...
    async def async_initialize(self) -> None: ...
    async def async_setup(self, entry_id: str) -> bool: ...
    async def async_unload(self, entry_id: str) -> bool: ...
    def async_schedule_reload(self, entry_id: str) -> None: ...
    async def async_reload(self, entry_id: str) -> bool: ...
    async def async_set_disabled_by(self, entry_id: str, disabled_by: ConfigEntryDisabler | None) -> bool: ...
    def async_update_entry(self, entry: ConfigEntry, *, data: Mapping[str, Any] | UndefinedType = ..., minor_version: int | UndefinedType = ..., options: Mapping[str, Any] | UndefinedType = ..., pref_disable_new_entities: bool | UndefinedType = ..., pref_disable_polling: bool | UndefinedType = ..., title: str | UndefinedType = ..., unique_id: str | None | UndefinedType = ..., version: int | UndefinedType = ...) -> bool: ...
    def _async_dispatch(self, change_type: ConfigEntryChange, entry: ConfigEntry) -> None: ...
    async def async_forward_entry_setups(self, entry: ConfigEntry, platforms: Iterable[Platform | str]) -> None: ...
    async def async_forward_entry_setup(self, entry: ConfigEntry, domain: Platform | str) -> bool: ...
    async def _async_forward_entry_setup(self, entry: ConfigEntry, domain: Platform | str, preload_platform: bool) -> bool: ...
    async def async_unload_platforms(self, entry: ConfigEntry, platforms: Iterable[Platform | str]) -> bool: ...
    async def async_forward_entry_unload(self, entry: ConfigEntry, domain: Platform | str) -> bool: ...
    def _async_schedule_save(self) -> None: ...
    def _data_to_save(self) -> dict[str, list[dict[str, Any]]]: ...
    async def async_wait_component(self, entry: ConfigEntry) -> bool: ...

async def _old_conf_migrator(old_config: dict[str, Any]) -> dict[str, Any]: ...
def _async_abort_entries_match(other_entries: list[ConfigEntry], match_dict: dict[str, Any] | None = None) -> None: ...

class ConfigEntryBaseFlow(data_entry_flow.FlowHandler[ConfigFlowResult, str]):
    _flow_result = ConfigFlowResult

class ConfigFlow(ConfigEntryBaseFlow):
    def __init_subclass__(cls, *, domain: str | None = None, **kwargs: Any) -> None: ...
    @property
    def unique_id(self) -> str | None: ...
    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow: ...
    @classmethod
    def async_supports_options_flow(cls, config_entry: ConfigEntry) -> bool: ...
    def _async_abort_entries_match(self, match_dict: dict[str, Any] | None = None) -> None: ...
    def _abort_if_unique_id_configured(self, updates: dict[str, Any] | None = None, reload_on_update: bool = True, *, error: str = 'already_configured') -> None: ...
    async def async_set_unique_id(self, unique_id: str | None = None, *, raise_on_progress: bool = True) -> ConfigEntry | None: ...
    def _set_confirm_only(self) -> None: ...
    def _async_current_entries(self, include_ignore: bool | None = None) -> list[ConfigEntry]: ...
    def _async_current_ids(self, include_ignore: bool = True) -> set[str | None]: ...
    def _async_in_progress(self, include_uninitialized: bool = False, match_context: dict[str, Any] | None = None) -> list[ConfigFlowResult]: ...
    async def async_step_ignore(self, user_input: dict[str, Any]) -> ConfigFlowResult: ...
    async def async_step_unignore(self, user_input: dict[str, Any]) -> ConfigFlowResult: ...
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def _async_handle_discovery_without_unique_id(self) -> None: ...
    async def _async_step_discovery_without_unique_id(self) -> ConfigFlowResult: ...
    async def async_step_discovery(self, discovery_info: DiscoveryInfoType) -> ConfigFlowResult: ...
    def async_abort(self, *, reason: str, description_placeholders: Mapping[str, str] | None = None) -> ConfigFlowResult: ...
    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> ConfigFlowResult: ...
    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo) -> ConfigFlowResult: ...
    async def async_step_hassio(self, discovery_info: HassioServiceInfo) -> ConfigFlowResult: ...
    async def async_step_integration_discovery(self, discovery_info: DiscoveryInfoType) -> ConfigFlowResult: ...
    async def async_step_homekit(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult: ...
    async def async_step_mqtt(self, discovery_info: MqttServiceInfo) -> ConfigFlowResult: ...
    async def async_step_ssdp(self, discovery_info: SsdpServiceInfo) -> ConfigFlowResult: ...
    async def async_step_usb(self, discovery_info: UsbServiceInfo) -> ConfigFlowResult: ...
    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult: ...
    def async_create_entry(self, *, title: str, data: Mapping[str, Any], description: str | None = None, description_placeholders: Mapping[str, str] | None = None, options: Mapping[str, Any] | None = None) -> ConfigFlowResult: ...
    def async_update_reload_and_abort(self, entry: ConfigEntry, *, unique_id: str | None | UndefinedType = ..., title: str | UndefinedType = ..., data: Mapping[str, Any] | UndefinedType = ..., options: Mapping[str, Any] | UndefinedType = ..., reason: str = 'reauth_successful') -> ConfigFlowResult: ...

class OptionsFlowManager(data_entry_flow.FlowManager[ConfigFlowResult, str]):
    _flow_result = ConfigFlowResult
    def _async_get_config_entry(self, config_entry_id: str) -> ConfigEntry: ...
    async def async_create_flow(self, handler_key: str, *, context: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> OptionsFlow: ...
    async def async_finish_flow(self, flow: data_entry_flow.FlowHandler[ConfigFlowResult, str], result: ConfigFlowResult) -> ConfigFlowResult: ...
    async def _async_setup_preview(self, flow: data_entry_flow.FlowHandler[ConfigFlowResult, str]) -> None: ...

class OptionsFlow(ConfigEntryBaseFlow):
    handler: str
    def _async_abort_entries_match(self, match_dict: dict[str, Any] | None = None) -> None: ...

class OptionsFlowWithConfigEntry(OptionsFlow):
    _config_entry: Incomplete
    _options: Incomplete
    def __init__(self, config_entry: ConfigEntry) -> None: ...
    @property
    def config_entry(self) -> ConfigEntry: ...
    @property
    def options(self) -> dict[str, Any]: ...

class EntityRegistryDisabledHandler:
    hass: Incomplete
    registry: Incomplete
    changed: Incomplete
    _remove_call_later: Incomplete
    def __init__(self, hass: HomeAssistant) -> None: ...
    def async_setup(self) -> None: ...
    def _handle_entry_updated(self, event: Event) -> None: ...
    async def _handle_reload(self, _now: Any) -> None: ...

def _handle_entry_updated_filter(event_data: Mapping[str, Any]) -> bool: ...
async def support_entry_unload(hass: HomeAssistant, domain: str) -> bool: ...
async def support_remove_from_device(hass: HomeAssistant, domain: str) -> bool: ...
async def _support_single_config_entry_only(hass: HomeAssistant, domain: str) -> bool: ...
async def _load_integration(hass: HomeAssistant, domain: str, hass_config: ConfigType) -> None: ...
async def _async_get_flow_handler(hass: HomeAssistant, domain: str, hass_config: ConfigType) -> type[ConfigFlow]: ...
