from .const import CONF_DATA_TYPE as CONF_DATA_TYPE, CONF_DEVICE_ADDRESS as CONF_DEVICE_ADDRESS, CONF_FAN_MODE_REGISTER as CONF_FAN_MODE_REGISTER, CONF_FAN_MODE_VALUES as CONF_FAN_MODE_VALUES, CONF_HVAC_MODE_REGISTER as CONF_HVAC_MODE_REGISTER, CONF_HVAC_ONOFF_REGISTER as CONF_HVAC_ONOFF_REGISTER, CONF_INPUT_TYPE as CONF_INPUT_TYPE, CONF_LAZY_ERROR as CONF_LAZY_ERROR, CONF_RETRIES as CONF_RETRIES, CONF_SLAVE_COUNT as CONF_SLAVE_COUNT, CONF_SWAP as CONF_SWAP, CONF_SWAP_BYTE as CONF_SWAP_BYTE, CONF_SWAP_WORD as CONF_SWAP_WORD, CONF_SWAP_WORD_BYTE as CONF_SWAP_WORD_BYTE, CONF_TARGET_TEMP as CONF_TARGET_TEMP, CONF_VIRTUAL_COUNT as CONF_VIRTUAL_COUNT, CONF_WRITE_TYPE as CONF_WRITE_TYPE, DEFAULT_HUB as DEFAULT_HUB, DEFAULT_SCAN_INTERVAL as DEFAULT_SCAN_INTERVAL, DataType as DataType, PLATFORMS as PLATFORMS, SERIAL as SERIAL
from _typeshed import Incomplete
from homeassistant.components.climate import HVACMode as HVACMode
from homeassistant.const import CONF_ADDRESS as CONF_ADDRESS, CONF_COMMAND_OFF as CONF_COMMAND_OFF, CONF_COMMAND_ON as CONF_COMMAND_ON, CONF_COUNT as CONF_COUNT, CONF_HOST as CONF_HOST, CONF_NAME as CONF_NAME, CONF_PORT as CONF_PORT, CONF_SCAN_INTERVAL as CONF_SCAN_INTERVAL, CONF_SLAVE as CONF_SLAVE, CONF_STRUCTURE as CONF_STRUCTURE, CONF_TIMEOUT as CONF_TIMEOUT, CONF_TYPE as CONF_TYPE
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.helpers.issue_registry import IssueSeverity as IssueSeverity, async_create_issue as async_create_issue
from typing import Any, NamedTuple

_LOGGER: Incomplete

class ENTRY(NamedTuple):
    struct_id: Incomplete
    register_count: Incomplete
    validate_parm: Incomplete

ILLEGAL: str
OPTIONAL: str
DEMANDED: str

class PARM_IS_LEGAL(NamedTuple):
    count: Incomplete
    structure: Incomplete
    slave_count: Incomplete
    swap_byte: Incomplete
    swap_word: Incomplete

DEFAULT_STRUCT_FORMAT: Incomplete

def modbus_create_issue(hass: HomeAssistant, key: str, subs: list[str], err: str) -> None: ...
def struct_validator(config: dict[str, Any]) -> dict[str, Any]: ...
def hvac_fixedsize_reglist_validator(value: Any) -> list: ...
def nan_validator(value: Any) -> int: ...
def duplicate_fan_mode_validator(config: dict[str, Any]) -> dict: ...
def check_hvac_target_temp_registers(config: dict) -> dict: ...
def register_int_list_validator(value: Any) -> Any: ...
def validate_modbus(hass: HomeAssistant, hosts: set[str], hub_names: set[str], hub: dict, hub_name_inx: int) -> bool: ...
def validate_entity(hass: HomeAssistant, hub_name: str, component: str, entity: dict, minimum_scan_interval: int, ent_names: set[str], ent_addr: set[str]) -> bool: ...
def check_config(hass: HomeAssistant, config: dict) -> dict: ...
