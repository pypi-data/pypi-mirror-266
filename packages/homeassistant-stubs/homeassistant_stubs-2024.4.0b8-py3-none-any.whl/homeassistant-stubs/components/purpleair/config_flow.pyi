import voluptuous as vol
from .const import CONF_SENSOR_INDICES as CONF_SENSOR_INDICES, DOMAIN as DOMAIN, LOGGER as LOGGER
from _typeshed import Incomplete
from aiopurpleair import API
from aiopurpleair.endpoints.sensors import NearbySensorResult as NearbySensorResult
from collections.abc import Mapping
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry as ConfigEntry, ConfigFlow as ConfigFlow, ConfigFlowResult as ConfigFlowResult, OptionsFlow as OptionsFlow
from homeassistant.const import CONF_API_KEY as CONF_API_KEY, CONF_LATITUDE as CONF_LATITUDE, CONF_LONGITUDE as CONF_LONGITUDE, CONF_SHOW_ON_MAP as CONF_SHOW_ON_MAP
from homeassistant.core import Event as Event, HomeAssistant as HomeAssistant, callback as callback
from homeassistant.helpers import aiohttp_client as aiohttp_client
from homeassistant.helpers.event import EventStateChangedData as EventStateChangedData, async_track_state_change_event as async_track_state_change_event
from homeassistant.helpers.selector import SelectOptionDict as SelectOptionDict, SelectSelector as SelectSelector, SelectSelectorConfig as SelectSelectorConfig, SelectSelectorMode as SelectSelectorMode
from typing import Any

CONF_DISTANCE: str
CONF_NEARBY_SENSOR_OPTIONS: str
CONF_SENSOR_DEVICE_ID: str
CONF_SENSOR_INDEX: str
DEFAULT_DISTANCE: int
API_KEY_SCHEMA: Incomplete

def async_get_api(hass: HomeAssistant, api_key: str) -> API: ...
def async_get_coordinates_schema(hass: HomeAssistant) -> vol.Schema: ...
def async_get_nearby_sensors_options(nearby_sensor_results: list[NearbySensorResult]) -> list[SelectOptionDict]: ...
def async_get_nearby_sensors_schema(options: list[SelectOptionDict]) -> vol.Schema: ...
def async_get_remove_sensor_options(hass: HomeAssistant, config_entry: ConfigEntry) -> list[SelectOptionDict]: ...
def async_get_remove_sensor_schema(sensors: list[SelectOptionDict]) -> vol.Schema: ...

@dataclass
class ValidationResult:
    data: Any = ...
    errors: dict[str, Any] = ...
    def __init__(self, data, errors) -> None: ...

async def async_validate_api_key(hass: HomeAssistant, api_key: str) -> ValidationResult: ...
async def async_validate_coordinates(hass: HomeAssistant, api_key: str, latitude: float, longitude: float, distance: float) -> ValidationResult: ...

class PurpleAirConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION: int
    _flow_data: Incomplete
    _reauth_entry: Incomplete
    def __init__(self) -> None: ...
    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> PurpleAirOptionsFlowHandler: ...
    async def async_step_by_coordinates(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_choose_sensor(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult: ...
    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...

class PurpleAirOptionsFlowHandler(OptionsFlow):
    _flow_data: Incomplete
    config_entry: Incomplete
    def __init__(self, config_entry: ConfigEntry) -> None: ...
    @property
    def settings_schema(self) -> vol.Schema: ...
    async def async_step_add_sensor(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_choose_sensor(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_remove_sensor(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
