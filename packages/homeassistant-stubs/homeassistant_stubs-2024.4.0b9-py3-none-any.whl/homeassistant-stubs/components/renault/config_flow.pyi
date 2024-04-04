from .const import CONF_KAMEREON_ACCOUNT_ID as CONF_KAMEREON_ACCOUNT_ID, CONF_LOCALE as CONF_LOCALE, DOMAIN as DOMAIN
from .renault_hub import RenaultHub as RenaultHub
from _typeshed import Incomplete
from collections.abc import Mapping
from homeassistant.config_entries import ConfigFlow as ConfigFlow, ConfigFlowResult as ConfigFlowResult
from homeassistant.const import CONF_PASSWORD as CONF_PASSWORD, CONF_USERNAME as CONF_USERNAME
from typing import Any

class RenaultFlowHandler(ConfigFlow, domain=DOMAIN):
    VERSION: int
    _original_data: Incomplete
    renault_config: Incomplete
    renault_hub: Incomplete
    def __init__(self) -> None: ...
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    def _show_user_form(self, errors: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_kamereon(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult: ...
    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    def _show_reauth_confirm_form(self, errors: dict[str, Any] | None = None) -> ConfigFlowResult: ...
