from .const import CONF_ALLOW_BANDWIDTH_SENSORS as CONF_ALLOW_BANDWIDTH_SENSORS, CONF_ALLOW_UPTIME_SENSORS as CONF_ALLOW_UPTIME_SENSORS, CONF_BLOCK_CLIENT as CONF_BLOCK_CLIENT, CONF_CLIENT_SOURCE as CONF_CLIENT_SOURCE, CONF_DETECTION_TIME as CONF_DETECTION_TIME, CONF_DPI_RESTRICTIONS as CONF_DPI_RESTRICTIONS, CONF_IGNORE_WIRED_BUG as CONF_IGNORE_WIRED_BUG, CONF_SITE_ID as CONF_SITE_ID, CONF_SSID_FILTER as CONF_SSID_FILTER, CONF_TRACK_CLIENTS as CONF_TRACK_CLIENTS, CONF_TRACK_DEVICES as CONF_TRACK_DEVICES, CONF_TRACK_WIRED_CLIENTS as CONF_TRACK_WIRED_CLIENTS, DEFAULT_DPI_RESTRICTIONS as DEFAULT_DPI_RESTRICTIONS, DOMAIN as UNIFI_DOMAIN
from .errors import AuthenticationRequired as AuthenticationRequired, CannotConnect as CannotConnect
from .hub import UnifiHub as UnifiHub, get_unifi_api as get_unifi_api
from _typeshed import Incomplete
from aiounifi.interfaces.sites import Sites as Sites
from collections.abc import Mapping
from homeassistant.components import ssdp as ssdp
from homeassistant.config_entries import ConfigEntry as ConfigEntry, ConfigFlow as ConfigFlow, ConfigFlowResult as ConfigFlowResult, OptionsFlow as OptionsFlow
from homeassistant.const import CONF_HOST as CONF_HOST, CONF_PASSWORD as CONF_PASSWORD, CONF_PORT as CONF_PORT, CONF_USERNAME as CONF_USERNAME, CONF_VERIFY_SSL as CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant as HomeAssistant, callback as callback
from homeassistant.helpers.device_registry import format_mac as format_mac
from typing import Any

DEFAULT_PORT: int
DEFAULT_SITE_ID: str
DEFAULT_VERIFY_SSL: bool
MODEL_PORTS: Incomplete

class UnifiFlowHandler(ConfigFlow, domain=UNIFI_DOMAIN):
    VERSION: int
    sites: Sites
    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> UnifiOptionsFlowHandler: ...
    config: Incomplete
    reauth_config_entry: Incomplete
    reauth_schema: Incomplete
    def __init__(self) -> None: ...
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_site(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult: ...
    async def async_step_ssdp(self, discovery_info: ssdp.SsdpServiceInfo) -> ConfigFlowResult: ...

class UnifiOptionsFlowHandler(OptionsFlow):
    hub: UnifiHub
    config_entry: Incomplete
    options: Incomplete
    def __init__(self, config_entry: ConfigEntry) -> None: ...
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_simple_options(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_configure_entity_sources(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_device_tracker(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_client_control(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_statistics_sensors(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def _update_options(self) -> ConfigFlowResult: ...

async def _async_discover_unifi(hass: HomeAssistant) -> str | None: ...
