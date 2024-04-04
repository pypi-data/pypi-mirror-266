from .translation import build_resources as build_resources
from _typeshed import Incomplete
from collections.abc import Iterable
from homeassistant.core import HomeAssistant as HomeAssistant, callback as callback
from homeassistant.loader import Integration as Integration, async_get_integrations as async_get_integrations
from homeassistant.util.json import load_json_object as load_json_object
from typing import Any

ICON_CACHE: str
_LOGGER: Incomplete

def _component_icons_path(component: str, integration: Integration) -> str | None: ...
def _load_icons_files(icons_files: dict[str, str]) -> dict[str, dict[str, Any]]: ...
async def _async_get_component_icons(hass: HomeAssistant, components: set[str], integrations: dict[str, Integration]) -> dict[str, Any]: ...

class _IconsCache:
    __slots__: Incomplete
    _hass: Incomplete
    _loaded: Incomplete
    _cache: Incomplete
    _lock: Incomplete
    def __init__(self, hass: HomeAssistant) -> None: ...
    async def async_fetch(self, category: str, components: set[str]) -> dict[str, dict[str, Any]]: ...
    async def _async_load(self, components: set[str]) -> None: ...
    def _build_category_cache(self, components: set[str], icons: dict[str, dict[str, Any]]) -> None: ...

async def async_get_icons(hass: HomeAssistant, category: str, integrations: Iterable[str] | None = None) -> dict[str, Any]: ...
def icon_for_battery_level(battery_level: int | None = None, charging: bool = False) -> str: ...
def icon_for_signal_level(signal_level: int | None = None) -> str: ...
