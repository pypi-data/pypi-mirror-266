import abc
from .const import DOMAIN as DOMAIN
from .coordinator import AirzoneUpdateCoordinator as AirzoneUpdateCoordinator
from .entity import AirzoneAidooEntity as AirzoneAidooEntity, AirzoneEntity as AirzoneEntity, AirzoneGroupEntity as AirzoneGroupEntity, AirzoneInstallationEntity as AirzoneInstallationEntity, AirzoneZoneEntity as AirzoneZoneEntity
from _typeshed import Incomplete
from aioairzone_cloud.common import OperationAction, OperationMode
from homeassistant.components.climate import ATTR_HVAC_MODE as ATTR_HVAC_MODE, ClimateEntity as ClimateEntity, ClimateEntityFeature as ClimateEntityFeature, FAN_AUTO as FAN_AUTO, FAN_HIGH as FAN_HIGH, FAN_LOW as FAN_LOW, FAN_MEDIUM as FAN_MEDIUM, HVACAction as HVACAction, HVACMode as HVACMode
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE as ATTR_TEMPERATURE, UnitOfTemperature as UnitOfTemperature
from homeassistant.core import HomeAssistant as HomeAssistant, callback as callback
from homeassistant.exceptions import HomeAssistantError as HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback as AddEntitiesCallback
from typing import Any, Final

FAN_SPEED_AUTO: dict[int, str]
FAN_SPEED_MAPS: Final[dict[int, dict[int, str]]]
HVAC_ACTION_LIB_TO_HASS: Final[dict[OperationAction, HVACAction]]
HVAC_MODE_LIB_TO_HASS: Final[dict[OperationMode, HVACMode]]
HVAC_MODE_HASS_TO_LIB: Final[dict[HVACMode, OperationMode]]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None: ...

class AirzoneClimate(AirzoneEntity, ClimateEntity, metaclass=abc.ABCMeta):
    _attr_name: Incomplete
    _attr_temperature_unit: Incomplete
    _enable_turn_on_off_backwards_compatibility: bool
    def _handle_coordinator_update(self) -> None: ...
    _attr_current_temperature: Incomplete
    _attr_current_humidity: Incomplete
    _attr_hvac_action: Incomplete
    _attr_hvac_mode: Incomplete
    _attr_max_temp: Incomplete
    _attr_min_temp: Incomplete
    _attr_target_temperature: Incomplete
    def _async_update_attrs(self) -> None: ...

class AirzoneDeviceClimate(AirzoneClimate, metaclass=abc.ABCMeta):
    _attr_supported_features: Incomplete
    async def async_turn_on(self) -> None: ...
    async def async_turn_off(self) -> None: ...
    async def async_set_temperature(self, **kwargs: Any) -> None: ...

class AirzoneDeviceGroupClimate(AirzoneClimate, metaclass=abc.ABCMeta):
    _attr_supported_features: Incomplete
    async def async_turn_on(self) -> None: ...
    async def async_turn_off(self) -> None: ...
    async def async_set_temperature(self, **kwargs: Any) -> None: ...
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None: ...

class AirzoneAidooClimate(AirzoneAidooEntity, AirzoneDeviceClimate):
    _speeds: dict[int, str]
    _speeds_reverse: dict[str, int]
    _attr_unique_id: Incomplete
    _attr_target_temperature_step: Incomplete
    _attr_hvac_modes: Incomplete
    def __init__(self, coordinator: AirzoneUpdateCoordinator, aidoo_id: str, aidoo_data: dict) -> None: ...
    _attr_fan_modes: Incomplete
    def _initialize_fan_speeds(self) -> None: ...
    async def async_set_fan_mode(self, fan_mode: str) -> None: ...
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None: ...
    _attr_fan_mode: Incomplete
    def _async_update_attrs(self) -> None: ...

class AirzoneGroupClimate(AirzoneGroupEntity, AirzoneDeviceGroupClimate):
    _attr_unique_id: Incomplete
    _attr_target_temperature_step: Incomplete
    _attr_hvac_modes: Incomplete
    def __init__(self, coordinator: AirzoneUpdateCoordinator, group_id: str, group_data: dict) -> None: ...

class AirzoneInstallationClimate(AirzoneInstallationEntity, AirzoneDeviceGroupClimate):
    _attr_unique_id: Incomplete
    _attr_target_temperature_step: Incomplete
    _attr_hvac_modes: Incomplete
    def __init__(self, coordinator: AirzoneUpdateCoordinator, inst_id: str, inst_data: dict) -> None: ...

class AirzoneZoneClimate(AirzoneZoneEntity, AirzoneDeviceClimate):
    _attr_unique_id: Incomplete
    _attr_target_temperature_step: Incomplete
    _attr_hvac_modes: Incomplete
    def __init__(self, coordinator: AirzoneUpdateCoordinator, system_zone_id: str, zone_data: dict) -> None: ...
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None: ...
