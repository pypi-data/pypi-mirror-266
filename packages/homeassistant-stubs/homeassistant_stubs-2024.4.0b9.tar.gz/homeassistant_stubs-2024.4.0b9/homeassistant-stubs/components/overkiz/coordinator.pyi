import logging
from .const import DOMAIN as DOMAIN, LOGGER as LOGGER, UPDATE_INTERVAL as UPDATE_INTERVAL
from _typeshed import Incomplete
from collections.abc import Callable as Callable, Coroutine
from datetime import timedelta
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed as ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator as DataUpdateCoordinator, UpdateFailed as UpdateFailed
from homeassistant.util.decorator import Registry as Registry
from pyoverkiz.client import OverkizClient as OverkizClient
from pyoverkiz.models import Device, Event as Event, Place
from typing import Any

EVENT_HANDLERS: Registry[str, Callable[[OverkizDataUpdateCoordinator, Event], Coroutine[Any, Any, None]]]

class OverkizDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Device]]):
    data: Incomplete
    client: Incomplete
    devices: Incomplete
    is_stateless: Incomplete
    executions: Incomplete
    areas: Incomplete
    config_entry_id: Incomplete
    def __init__(self, hass: HomeAssistant, logger: logging.Logger, *, name: str, client: OverkizClient, devices: list[Device], places: Place | None, update_interval: timedelta | None = None, config_entry_id: str) -> None: ...
    update_interval: Incomplete
    async def _async_update_data(self) -> dict[str, Device]: ...
    async def _get_devices(self) -> dict[str, Device]: ...
    def _places_to_area(self, place: Place) -> dict[str, str]: ...

async def on_device_available(coordinator: OverkizDataUpdateCoordinator, event: Event) -> None: ...
async def on_device_unavailable_disabled(coordinator: OverkizDataUpdateCoordinator, event: Event) -> None: ...
async def on_device_created_updated(coordinator: OverkizDataUpdateCoordinator, event: Event) -> None: ...
async def on_device_state_changed(coordinator: OverkizDataUpdateCoordinator, event: Event) -> None: ...
async def on_device_removed(coordinator: OverkizDataUpdateCoordinator, event: Event) -> None: ...
async def on_execution_registered(coordinator: OverkizDataUpdateCoordinator, event: Event) -> None: ...
async def on_execution_state_changed(coordinator: OverkizDataUpdateCoordinator, event: Event) -> None: ...
