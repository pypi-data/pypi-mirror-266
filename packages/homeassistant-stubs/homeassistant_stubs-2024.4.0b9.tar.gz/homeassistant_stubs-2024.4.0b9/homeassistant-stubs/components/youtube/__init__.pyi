from .api import AsyncConfigEntryAuth as AsyncConfigEntryAuth
from .const import AUTH as AUTH, COORDINATOR as COORDINATOR, DOMAIN as DOMAIN
from .coordinator import YouTubeDataUpdateCoordinator as YouTubeDataUpdateCoordinator
from _typeshed import Incomplete
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import Platform as Platform
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed as ConfigEntryAuthFailed, ConfigEntryNotReady as ConfigEntryNotReady
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session as OAuth2Session, async_get_config_entry_implementation as async_get_config_entry_implementation

PLATFORMS: Incomplete

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool: ...
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool: ...
async def delete_devices(hass: HomeAssistant, entry: ConfigEntry, coordinator: YouTubeDataUpdateCoordinator) -> None: ...
