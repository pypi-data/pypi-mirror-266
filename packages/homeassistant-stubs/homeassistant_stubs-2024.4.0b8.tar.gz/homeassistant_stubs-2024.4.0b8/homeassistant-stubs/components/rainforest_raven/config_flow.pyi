from .const import DEFAULT_NAME as DEFAULT_NAME, DOMAIN as DOMAIN
from _typeshed import Incomplete
from homeassistant.components import usb as usb
from homeassistant.config_entries import ConfigFlow as ConfigFlow, ConfigFlowResult as ConfigFlowResult
from homeassistant.const import CONF_DEVICE as CONF_DEVICE, CONF_MAC as CONF_MAC, CONF_NAME as CONF_NAME
from homeassistant.helpers.selector import SelectSelector as SelectSelector, SelectSelectorConfig as SelectSelectorConfig, SelectSelectorMode as SelectSelectorMode
from serial.tools.list_ports_common import ListPortInfo as ListPortInfo
from typing import Any

def _format_id(value: str | int) -> str: ...
def _generate_unique_id(info: ListPortInfo | usb.UsbServiceInfo) -> str: ...

class RainforestRavenConfigFlow(ConfigFlow, domain=DOMAIN):
    _dev_path: Incomplete
    _meter_macs: Incomplete
    def __init__(self) -> None: ...
    async def _validate_device(self, dev_path: str) -> None: ...
    async def async_step_meters(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
    async def async_step_usb(self, discovery_info: usb.UsbServiceInfo) -> ConfigFlowResult: ...
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult: ...
