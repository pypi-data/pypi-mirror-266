import voluptuous as vol
from .const import DEFAULT_PORT as DEFAULT_PORT, DOMAIN as DOMAIN
from _typeshed import Incomplete
from aiovlc.client import Client
from collections.abc import Mapping
from homeassistant.components.hassio import HassioServiceInfo as HassioServiceInfo
from homeassistant.config_entries import ConfigEntry as ConfigEntry, ConfigFlow as ConfigFlow, ConfigFlowResult as ConfigFlowResult
from homeassistant.const import CONF_HOST as CONF_HOST, CONF_NAME as CONF_NAME, CONF_PASSWORD as CONF_PASSWORD, CONF_PORT as CONF_PORT
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.exceptions import HomeAssistantError as HomeAssistantError
from typing import Any

_LOGGER: Incomplete

def user_form_schema(user_input: dict[str, Any] | None) -> vol.Schema: ...

STEP_REAUTH_DATA_SCHEMA: Incomplete

async def vlc_connect(vlc: Client) -> None: ...
async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]: ...

class VLCTelnetConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION: int
    entry: ConfigEntry | None
    hassio_discovery: dict[str, Any] | None
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult: ...
    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_hassio(self, discovery_info: HassioServiceInfo) -> ConfigFlowResult: ...
    async def async_step_hassio_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...

class CannotConnect(HomeAssistantError): ...
class InvalidAuth(HomeAssistantError): ...
