import voluptuous as vol
from .const import CONF_ARRIVAL_TIME as CONF_ARRIVAL_TIME, CONF_DEPARTURE_TIME as CONF_DEPARTURE_TIME, CONF_DESTINATION as CONF_DESTINATION, CONF_DESTINATION_ENTITY_ID as CONF_DESTINATION_ENTITY_ID, CONF_DESTINATION_LATITUDE as CONF_DESTINATION_LATITUDE, CONF_DESTINATION_LONGITUDE as CONF_DESTINATION_LONGITUDE, CONF_ORIGIN as CONF_ORIGIN, CONF_ORIGIN_ENTITY_ID as CONF_ORIGIN_ENTITY_ID, CONF_ORIGIN_LATITUDE as CONF_ORIGIN_LATITUDE, CONF_ORIGIN_LONGITUDE as CONF_ORIGIN_LONGITUDE, CONF_ROUTE_MODE as CONF_ROUTE_MODE, DEFAULT_NAME as DEFAULT_NAME, DOMAIN as DOMAIN, ROUTE_MODES as ROUTE_MODES, ROUTE_MODE_FASTEST as ROUTE_MODE_FASTEST, TRAVEL_MODES as TRAVEL_MODES, TRAVEL_MODE_CAR as TRAVEL_MODE_CAR, TRAVEL_MODE_PUBLIC as TRAVEL_MODE_PUBLIC
from _typeshed import Incomplete
from homeassistant.config_entries import ConfigEntry as ConfigEntry, ConfigFlow as ConfigFlow, ConfigFlowResult as ConfigFlowResult, OptionsFlow as OptionsFlow
from homeassistant.const import CONF_API_KEY as CONF_API_KEY, CONF_LATITUDE as CONF_LATITUDE, CONF_LONGITUDE as CONF_LONGITUDE, CONF_MODE as CONF_MODE, CONF_NAME as CONF_NAME
from homeassistant.core import callback as callback
from homeassistant.helpers.selector import EntitySelector as EntitySelector, LocationSelector as LocationSelector, TimeSelector as TimeSelector
from typing import Any

_LOGGER: Incomplete
DEFAULT_OPTIONS: Incomplete

async def async_validate_api_key(api_key: str) -> None: ...
def get_user_step_schema(data: dict[str, Any]) -> vol.Schema: ...

class HERETravelTimeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION: int
    _config: Incomplete
    def __init__(self) -> None: ...
    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> HERETravelTimeOptionsFlow: ...
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_origin_menu(self, _: None = None) -> ConfigFlowResult: ...
    async def async_step_origin_coordinates(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_destination_menu(self, _: None = None) -> ConfigFlowResult: ...
    async def async_step_origin_entity(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_destination_coordinates(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_destination_entity(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...

class HERETravelTimeOptionsFlow(OptionsFlow):
    config_entry: Incomplete
    _config: Incomplete
    def __init__(self, config_entry: ConfigEntry) -> None: ...
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_time_menu(self, _: None = None) -> ConfigFlowResult: ...
    async def async_step_no_time(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_arrival_time(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_departure_time(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
