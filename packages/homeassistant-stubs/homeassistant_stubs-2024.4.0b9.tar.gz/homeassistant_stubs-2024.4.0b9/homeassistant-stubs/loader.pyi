import pathlib
import voluptuous as vol
from . import generated as generated
from .config_entries import ConfigEntry as ConfigEntry
from .const import Platform as Platform
from .core import HomeAssistant as HomeAssistant, callback as callback
from .generated.application_credentials import APPLICATION_CREDENTIALS as APPLICATION_CREDENTIALS
from .generated.bluetooth import BLUETOOTH as BLUETOOTH
from .generated.config_flows import FLOWS as FLOWS
from .generated.dhcp import DHCP as DHCP
from .generated.mqtt import MQTT as MQTT
from .generated.ssdp import SSDP as SSDP
from .generated.usb import USB as USB
from .generated.zeroconf import HOMEKIT as HOMEKIT, ZEROCONF as ZEROCONF
from .helpers import device_registry as dr
from .helpers.typing import ConfigType as ConfigType
from .util.json import JSON_DECODE_EXCEPTIONS as JSON_DECODE_EXCEPTIONS, json_loads as json_loads
from _typeshed import Incomplete
from awesomeversion import AwesomeVersion
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cached_property as cached_property
from types import ModuleType
from typing import Any, Literal, Protocol, TypeVar, TypedDict

_CallableT = TypeVar('_CallableT', bound=Callable[..., Any])
_LOGGER: Incomplete
BASE_PRELOAD_PLATFORMS: Incomplete

@dataclass
class BlockedIntegration:
    lowest_good_version: AwesomeVersion | None
    reason: str
    def __init__(self, lowest_good_version, reason) -> None: ...

BLOCKED_CUSTOM_INTEGRATIONS: dict[str, BlockedIntegration]
DATA_COMPONENTS: str
DATA_INTEGRATIONS: str
DATA_MISSING_PLATFORMS: str
DATA_CUSTOM_COMPONENTS: str
DATA_PRELOAD_PLATFORMS: str
PACKAGE_CUSTOM_COMPONENTS: str
PACKAGE_BUILTIN: str
CUSTOM_WARNING: str
IMPORT_EVENT_LOOP_WARNING: str
_UNDEF: Incomplete
MOVED_ZEROCONF_PROPS: Incomplete

class DHCPMatcherRequired(TypedDict, total=True):
    domain: str

class DHCPMatcherOptional(TypedDict, total=False):
    macaddress: str
    hostname: str
    registered_devices: bool

class DHCPMatcher(DHCPMatcherRequired, DHCPMatcherOptional): ...

class BluetoothMatcherRequired(TypedDict, total=True):
    domain: str

class BluetoothMatcherOptional(TypedDict, total=False):
    local_name: str
    service_uuid: str
    service_data_uuid: str
    manufacturer_id: int
    manufacturer_data_start: list[int]
    connectable: bool

class BluetoothMatcher(BluetoothMatcherRequired, BluetoothMatcherOptional): ...

class USBMatcherRequired(TypedDict, total=True):
    domain: str

class USBMatcherOptional(TypedDict, total=False):
    vid: str
    pid: str
    serial_number: str
    manufacturer: str
    description: str

class USBMatcher(USBMatcherRequired, USBMatcherOptional): ...

@dataclass(slots=True)
class HomeKitDiscoveredIntegration:
    domain: str
    always_discover: bool
    def __init__(self, domain, always_discover) -> None: ...

class ZeroconfMatcher(TypedDict, total=False):
    domain: str
    name: str
    properties: dict[str, str]

class Manifest(TypedDict, total=False):
    name: str
    disabled: str
    domain: str
    integration_type: Literal['entity', 'device', 'hardware', 'helper', 'hub', 'service', 'system', 'virtual']
    dependencies: list[str]
    after_dependencies: list[str]
    requirements: list[str]
    config_flow: bool
    documentation: str
    issue_tracker: str
    quality_scale: str
    iot_class: str
    bluetooth: list[dict[str, int | str]]
    mqtt: list[str]
    ssdp: list[dict[str, str]]
    zeroconf: list[str | dict[str, str]]
    dhcp: list[dict[str, bool | str]]
    usb: list[dict[str, str]]
    homekit: dict[str, list[str]]
    is_built_in: bool
    version: str
    codeowners: list[str]
    loggers: list[str]
    import_executor: bool
    single_config_entry: bool

def async_setup(hass: HomeAssistant) -> None: ...
def manifest_from_legacy_module(domain: str, module: ModuleType) -> Manifest: ...
async def _async_get_custom_components(hass: HomeAssistant) -> dict[str, Integration]: ...
async def async_get_custom_components(hass: HomeAssistant) -> dict[str, Integration]: ...
async def async_get_config_flows(hass: HomeAssistant, type_filter: Literal['device', 'helper', 'hub', 'service'] | None = None) -> set[str]: ...

class ComponentProtocol(Protocol):
    CONFIG_SCHEMA: vol.Schema
    DOMAIN: str
    async def async_setup_entry(self, hass: HomeAssistant, config_entry: ConfigEntry) -> bool: ...
    async def async_unload_entry(self, hass: HomeAssistant, config_entry: ConfigEntry) -> bool: ...
    async def async_migrate_entry(self, hass: HomeAssistant, config_entry: ConfigEntry) -> bool: ...
    async def async_remove_entry(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None: ...
    async def async_remove_config_entry_device(self, hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry) -> bool: ...
    async def async_reset_platform(self, hass: HomeAssistant, integration_name: str) -> None: ...
    async def async_setup(self, hass: HomeAssistant, config: ConfigType) -> bool: ...
    def setup(self, hass: HomeAssistant, config: ConfigType) -> bool: ...

async def async_get_integration_descriptions(hass: HomeAssistant) -> dict[str, Any]: ...
async def async_get_application_credentials(hass: HomeAssistant) -> list[str]: ...
def async_process_zeroconf_match_dict(entry: dict[str, Any]) -> ZeroconfMatcher: ...
async def async_get_zeroconf(hass: HomeAssistant) -> dict[str, list[ZeroconfMatcher]]: ...
async def async_get_bluetooth(hass: HomeAssistant) -> list[BluetoothMatcher]: ...
async def async_get_dhcp(hass: HomeAssistant) -> list[DHCPMatcher]: ...
async def async_get_usb(hass: HomeAssistant) -> list[USBMatcher]: ...
def homekit_always_discover(iot_class: str | None) -> bool: ...
async def async_get_homekit(hass: HomeAssistant) -> dict[str, HomeKitDiscoveredIntegration]: ...
async def async_get_ssdp(hass: HomeAssistant) -> dict[str, list[dict[str, str]]]: ...
async def async_get_mqtt(hass: HomeAssistant) -> dict[str, list[str]]: ...
def async_register_preload_platform(hass: HomeAssistant, platform_name: str) -> None: ...

class Integration:
    @classmethod
    def resolve_from_root(cls, hass: HomeAssistant, root_module: ModuleType, domain: str) -> Integration | None: ...
    hass: Incomplete
    pkg_path: Incomplete
    file_path: Incomplete
    manifest: Incomplete
    _all_dependencies_resolved: Incomplete
    _all_dependencies: Incomplete
    _platforms_to_preload: Incomplete
    _component_future: Incomplete
    _import_futures: Incomplete
    _cache: Incomplete
    _missing_platforms_cache: Incomplete
    _top_level_files: Incomplete
    def __init__(self, hass: HomeAssistant, pkg_path: str, file_path: pathlib.Path, manifest: Manifest, top_level_files: set[str] | None = None) -> None: ...
    @cached_property
    def name(self) -> str: ...
    @cached_property
    def disabled(self) -> str | None: ...
    @cached_property
    def domain(self) -> str: ...
    @cached_property
    def dependencies(self) -> list[str]: ...
    @cached_property
    def after_dependencies(self) -> list[str]: ...
    @cached_property
    def requirements(self) -> list[str]: ...
    @cached_property
    def config_flow(self) -> bool: ...
    @cached_property
    def documentation(self) -> str | None: ...
    @cached_property
    def issue_tracker(self) -> str | None: ...
    @cached_property
    def loggers(self) -> list[str] | None: ...
    @cached_property
    def quality_scale(self) -> str | None: ...
    @cached_property
    def iot_class(self) -> str | None: ...
    @cached_property
    def integration_type(self) -> Literal['entity', 'device', 'hardware', 'helper', 'hub', 'service', 'system', 'virtual']: ...
    @cached_property
    def import_executor(self) -> bool: ...
    @cached_property
    def has_translations(self) -> bool: ...
    @cached_property
    def has_services(self) -> bool: ...
    @property
    def mqtt(self) -> list[str] | None: ...
    @property
    def ssdp(self) -> list[dict[str, str]] | None: ...
    @property
    def zeroconf(self) -> list[str | dict[str, str]] | None: ...
    @property
    def bluetooth(self) -> list[dict[str, str | int]] | None: ...
    @property
    def dhcp(self) -> list[dict[str, str | bool]] | None: ...
    @property
    def usb(self) -> list[dict[str, str]] | None: ...
    @property
    def homekit(self) -> dict[str, list[str]] | None: ...
    @property
    def is_built_in(self) -> bool: ...
    @property
    def version(self) -> AwesomeVersion | None: ...
    @cached_property
    def single_config_entry(self) -> bool: ...
    @property
    def all_dependencies(self) -> set[str]: ...
    @property
    def all_dependencies_resolved(self) -> bool: ...
    async def resolve_dependencies(self) -> bool: ...
    async def async_get_component(self) -> ComponentProtocol: ...
    def get_component(self) -> ComponentProtocol: ...
    def _get_component(self, preload_platforms: bool = False) -> ComponentProtocol: ...
    def _load_platforms(self, platform_names: Iterable[str]) -> dict[str, ModuleType]: ...
    async def async_get_platform(self, platform_name: str) -> ModuleType: ...
    async def async_get_platforms(self, platform_names: Iterable[Platform | str]) -> dict[str, ModuleType]: ...
    def _get_platform_cached_or_raise(self, platform_name: str) -> ModuleType | None: ...
    def platforms_are_loaded(self, platform_names: Iterable[str]) -> bool: ...
    def get_platform_cached(self, platform_name: str) -> ModuleType | None: ...
    def get_platform(self, platform_name: str) -> ModuleType: ...
    def platforms_exists(self, platform_names: Iterable[str]) -> list[str]: ...
    def _load_platform(self, platform_name: str) -> ModuleType: ...
    def _import_platform(self, platform_name: str) -> ModuleType: ...
    def __repr__(self) -> str: ...

def _version_blocked(integration_version: AwesomeVersion, blocked_integration: BlockedIntegration) -> bool: ...
def _resolve_integrations_from_root(hass: HomeAssistant, root_module: ModuleType, domains: Iterable[str]) -> dict[str, Integration]: ...
def async_get_loaded_integration(hass: HomeAssistant, domain: str) -> Integration: ...
async def async_get_integration(hass: HomeAssistant, domain: str) -> Integration: ...
async def async_get_integrations(hass: HomeAssistant, domains: Iterable[str]) -> dict[str, Integration | Exception]: ...

class LoaderError(Exception): ...

class IntegrationNotFound(LoaderError):
    domain: Incomplete
    def __init__(self, domain: str) -> None: ...

class IntegrationNotLoaded(LoaderError):
    domain: Incomplete
    def __init__(self, domain: str) -> None: ...

class CircularDependency(LoaderError):
    from_domain: Incomplete
    to_domain: Incomplete
    def __init__(self, from_domain: str | set[str], to_domain: str) -> None: ...

def _load_file(hass: HomeAssistant, comp_or_platform: str, base_paths: list[str]) -> ComponentProtocol | None: ...

class ModuleWrapper:
    _hass: Incomplete
    _module: Incomplete
    def __init__(self, hass: HomeAssistant, module: ComponentProtocol) -> None: ...
    def __getattr__(self, attr: str) -> Any: ...

class Components:
    _hass: Incomplete
    def __init__(self, hass: HomeAssistant) -> None: ...
    def __getattr__(self, comp_name: str) -> ModuleWrapper: ...

class Helpers:
    _hass: Incomplete
    def __init__(self, hass: HomeAssistant) -> None: ...
    def __getattr__(self, helper_name: str) -> ModuleWrapper: ...

def bind_hass(func: _CallableT) -> _CallableT: ...
async def _async_component_dependencies(hass: HomeAssistant, integration: Integration) -> set[str]: ...
def _async_mount_config_dir(hass: HomeAssistant) -> None: ...
def _lookup_path(hass: HomeAssistant) -> list[str]: ...
def is_component_module_loaded(hass: HomeAssistant, module: str) -> bool: ...
def async_get_issue_tracker(hass: HomeAssistant | None, *, integration: Integration | None = None, integration_domain: str | None = None, module: str | None = None) -> str | None: ...
def async_suggest_report_issue(hass: HomeAssistant | None, *, integration: Integration | None = None, integration_domain: str | None = None, module: str | None = None) -> str: ...
