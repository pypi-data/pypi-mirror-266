from .bridge import AsusWrtBridge as AsusWrtBridge, WrtDevice as WrtDevice
from .const import CONF_DNSMASQ as CONF_DNSMASQ, CONF_INTERFACE as CONF_INTERFACE, CONF_REQUIRE_IP as CONF_REQUIRE_IP, CONF_TRACK_UNKNOWN as CONF_TRACK_UNKNOWN, DEFAULT_DNSMASQ as DEFAULT_DNSMASQ, DEFAULT_INTERFACE as DEFAULT_INTERFACE, DEFAULT_TRACK_UNKNOWN as DEFAULT_TRACK_UNKNOWN, DOMAIN as DOMAIN, KEY_COORDINATOR as KEY_COORDINATOR, KEY_METHOD as KEY_METHOD, KEY_SENSORS as KEY_SENSORS, SENSORS_CONNECTED_DEVICE as SENSORS_CONNECTED_DEVICE
from _typeshed import Incomplete
from collections.abc import Callable as Callable
from datetime import datetime
from homeassistant.components.device_tracker import CONF_CONSIDER_HOME as CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME as DEFAULT_CONSIDER_HOME
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.core import CALLBACK_TYPE as CALLBACK_TYPE, HomeAssistant as HomeAssistant, callback as callback
from homeassistant.exceptions import ConfigEntryNotReady as ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceInfo as DeviceInfo, format_mac as format_mac
from homeassistant.helpers.dispatcher import async_dispatcher_send as async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval as async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator as DataUpdateCoordinator
from homeassistant.util import slugify as slugify
from typing import Any

CONF_REQ_RELOAD: Incomplete
SCAN_INTERVAL: Incomplete
SENSORS_TYPE_COUNT: str
_LOGGER: Incomplete

class AsusWrtSensorDataHandler:
    _hass: Incomplete
    _api: Incomplete
    _connected_devices: int
    def __init__(self, hass: HomeAssistant, api: AsusWrtBridge) -> None: ...
    async def _get_connected_devices(self) -> dict[str, int]: ...
    def update_device_count(self, conn_devices: int) -> bool: ...
    async def get_coordinator(self, sensor_type: str, update_method: Callable[[], Any] | None = None) -> DataUpdateCoordinator: ...

class AsusWrtDevInfo:
    _mac: Incomplete
    _name: Incomplete
    _ip_address: Incomplete
    _last_activity: Incomplete
    _connected: bool
    def __init__(self, mac: str, name: str | None = None) -> None: ...
    def update(self, dev_info: WrtDevice | None = None, consider_home: int = 0) -> None: ...
    @property
    def is_connected(self) -> bool: ...
    @property
    def mac(self) -> str: ...
    @property
    def name(self) -> str | None: ...
    @property
    def ip_address(self) -> str | None: ...
    @property
    def last_activity(self) -> datetime | None: ...

class AsusWrtRouter:
    hass: Incomplete
    _entry: Incomplete
    _devices: Incomplete
    _connected_devices: int
    _connect_error: bool
    _sensors_data_handler: Incomplete
    _sensors_coordinator: Incomplete
    _on_close: Incomplete
    _options: Incomplete
    _api: Incomplete
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None: ...
    def _migrate_entities_unique_id(self) -> None: ...
    async def setup(self) -> None: ...
    async def update_all(self, now: datetime | None = None) -> None: ...
    async def update_devices(self) -> None: ...
    async def init_sensors_coordinator(self) -> None: ...
    async def _update_unpolled_sensors(self) -> None: ...
    async def close(self) -> None: ...
    def async_on_close(self, func: CALLBACK_TYPE) -> None: ...
    def update_options(self, new_options: dict[str, Any]) -> bool: ...
    @property
    def device_info(self) -> DeviceInfo: ...
    @property
    def signal_device_new(self) -> str: ...
    @property
    def signal_device_update(self) -> str: ...
    @property
    def host(self) -> str: ...
    @property
    def unique_id(self) -> str: ...
    @property
    def devices(self) -> dict[str, AsusWrtDevInfo]: ...
    @property
    def sensors_coordinator(self) -> dict[str, Any]: ...
