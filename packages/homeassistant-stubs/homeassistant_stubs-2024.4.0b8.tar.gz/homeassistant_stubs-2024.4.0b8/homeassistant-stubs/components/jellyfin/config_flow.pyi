from .client_wrapper import CannotConnect as CannotConnect, InvalidAuth as InvalidAuth, create_client as create_client, validate_input as validate_input
from .const import CONF_CLIENT_DEVICE_ID as CONF_CLIENT_DEVICE_ID, DOMAIN as DOMAIN
from _typeshed import Incomplete
from collections.abc import Mapping
from homeassistant.config_entries import ConfigEntry as ConfigEntry, ConfigFlow as ConfigFlow, ConfigFlowResult as ConfigFlowResult
from homeassistant.const import CONF_PASSWORD as CONF_PASSWORD, CONF_URL as CONF_URL, CONF_USERNAME as CONF_USERNAME
from homeassistant.util.uuid import random_uuid_hex as random_uuid_hex
from typing import Any

_LOGGER: Incomplete
STEP_USER_DATA_SCHEMA: Incomplete
REAUTH_DATA_SCHEMA: Incomplete

def _generate_client_device_id() -> str: ...

class JellyfinConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION: int
    client_device_id: Incomplete
    entry: Incomplete
    def __init__(self) -> None: ...
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult: ...
    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
