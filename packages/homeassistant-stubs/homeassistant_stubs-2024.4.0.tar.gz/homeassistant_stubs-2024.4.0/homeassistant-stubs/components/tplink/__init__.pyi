from .const import CONF_DEVICE_CONFIG as CONF_DEVICE_CONFIG, CONNECT_TIMEOUT as CONNECT_TIMEOUT, DISCOVERY_TIMEOUT as DISCOVERY_TIMEOUT, DOMAIN as DOMAIN, PLATFORMS as PLATFORMS
from .coordinator import TPLinkDataUpdateCoordinator as TPLinkDataUpdateCoordinator
from .models import TPLinkData as TPLinkData
from _typeshed import Incomplete
from aiohttp import ClientSession as ClientSession
from homeassistant import config_entries as config_entries
from homeassistant.components import network as network
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import CONF_ALIAS as CONF_ALIAS, CONF_AUTHENTICATION as CONF_AUTHENTICATION, CONF_HOST as CONF_HOST, CONF_MAC as CONF_MAC, CONF_MODEL as CONF_MODEL, CONF_PASSWORD as CONF_PASSWORD, CONF_USERNAME as CONF_USERNAME
from homeassistant.core import HomeAssistant as HomeAssistant, callback as callback
from homeassistant.exceptions import ConfigEntryAuthFailed as ConfigEntryAuthFailed, ConfigEntryNotReady as ConfigEntryNotReady
from homeassistant.helpers import discovery_flow as discovery_flow
from homeassistant.helpers.aiohttp_client import async_create_clientsession as async_create_clientsession
from homeassistant.helpers.event import async_track_time_interval as async_track_time_interval
from homeassistant.helpers.typing import ConfigType as ConfigType
from kasa import Credentials, SmartDevice

DISCOVERY_INTERVAL: Incomplete
CONFIG_SCHEMA: Incomplete
_LOGGER: Incomplete

def create_async_tplink_clientsession(hass: HomeAssistant) -> ClientSession: ...
def async_trigger_discovery(hass: HomeAssistant, discovered_devices: dict[str, SmartDevice]) -> None: ...
async def async_discover_devices(hass: HomeAssistant) -> dict[str, SmartDevice]: ...
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool: ...
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool: ...
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool: ...
def legacy_device_id(device: SmartDevice) -> str: ...
async def get_credentials(hass: HomeAssistant) -> Credentials | None: ...
async def set_credentials(hass: HomeAssistant, username: str, password: str) -> None: ...
def mac_alias(mac: str) -> str: ...
