import asyncio
from .const import ATTR_HOST_NAME as ATTR_HOST_NAME, ATTR_IP as ATTR_IP, ATTR_MAC as ATTR_MAC, ATTR_SOURCE_TYPE as ATTR_SOURCE_TYPE, CONNECTED_DEVICE_REGISTERED as CONNECTED_DEVICE_REGISTERED, DOMAIN as DOMAIN, LOGGER as LOGGER, SourceType as SourceType
from _typeshed import Incomplete
from homeassistant.components import zone as zone
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import ATTR_BATTERY_LEVEL as ATTR_BATTERY_LEVEL, ATTR_GPS_ACCURACY as ATTR_GPS_ACCURACY, ATTR_LATITUDE as ATTR_LATITUDE, ATTR_LONGITUDE as ATTR_LONGITUDE, EntityCategory as EntityCategory, STATE_HOME as STATE_HOME, STATE_NOT_HOME as STATE_NOT_HOME
from homeassistant.core import Event as Event, HomeAssistant as HomeAssistant, callback as callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo as DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send as async_dispatcher_send
from homeassistant.helpers.entity import Entity as Entity
from homeassistant.helpers.entity_component import EntityComponent as EntityComponent
from homeassistant.helpers.entity_platform import EntityPlatform as EntityPlatform
from homeassistant.helpers.typing import StateType as StateType

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool: ...
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool: ...
def _async_connected_device_registered(hass: HomeAssistant, mac: str, ip_address: str | None, hostname: str | None) -> None: ...
def _async_register_mac(hass: HomeAssistant, domain: str, mac: str, unique_id: str) -> None: ...

class BaseTrackerEntity(Entity):
    _attr_device_info: None
    _attr_entity_category: Incomplete
    @property
    def battery_level(self) -> int | None: ...
    @property
    def source_type(self) -> SourceType | str: ...
    @property
    def state_attributes(self) -> dict[str, StateType]: ...

class TrackerEntity(BaseTrackerEntity):
    @property
    def should_poll(self) -> bool: ...
    @property
    def force_update(self) -> bool: ...
    @property
    def location_accuracy(self) -> int: ...
    @property
    def location_name(self) -> str | None: ...
    @property
    def latitude(self) -> float | None: ...
    @property
    def longitude(self) -> float | None: ...
    @property
    def state(self) -> str | None: ...
    @property
    def state_attributes(self) -> dict[str, StateType]: ...

class ScannerEntity(BaseTrackerEntity):
    @property
    def ip_address(self) -> str | None: ...
    @property
    def mac_address(self) -> str | None: ...
    @property
    def hostname(self) -> str | None: ...
    @property
    def state(self) -> str: ...
    @property
    def is_connected(self) -> bool: ...
    @property
    def unique_id(self) -> str | None: ...
    @property
    def device_info(self) -> DeviceInfo | None: ...
    @property
    def entity_registry_enabled_default(self) -> bool: ...
    def add_to_platform_start(self, hass: HomeAssistant, platform: EntityPlatform, parallel_updates: asyncio.Semaphore | None) -> None: ...
    def find_device_entry(self) -> dr.DeviceEntry | None: ...
    registry_entry: Incomplete
    async def async_internal_added_to_hass(self) -> None: ...
    @property
    def state_attributes(self) -> dict[str, StateType]: ...
