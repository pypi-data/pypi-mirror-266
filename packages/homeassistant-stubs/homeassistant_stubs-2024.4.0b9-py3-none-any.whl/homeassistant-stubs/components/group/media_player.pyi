from _typeshed import Incomplete
from collections.abc import Callable as Callable, Mapping
from homeassistant.components.media_player import ATTR_MEDIA_CONTENT_ID as ATTR_MEDIA_CONTENT_ID, ATTR_MEDIA_CONTENT_TYPE as ATTR_MEDIA_CONTENT_TYPE, ATTR_MEDIA_SEEK_POSITION as ATTR_MEDIA_SEEK_POSITION, ATTR_MEDIA_SHUFFLE as ATTR_MEDIA_SHUFFLE, ATTR_MEDIA_VOLUME_LEVEL as ATTR_MEDIA_VOLUME_LEVEL, ATTR_MEDIA_VOLUME_MUTED as ATTR_MEDIA_VOLUME_MUTED, DOMAIN as DOMAIN, MediaPlayerEntity as MediaPlayerEntity, MediaPlayerEntityFeature as MediaPlayerEntityFeature, MediaPlayerState as MediaPlayerState, MediaType as MediaType, PLATFORM_SCHEMA as PLATFORM_SCHEMA, SERVICE_CLEAR_PLAYLIST as SERVICE_CLEAR_PLAYLIST, SERVICE_PLAY_MEDIA as SERVICE_PLAY_MEDIA
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID as ATTR_ENTITY_ID, ATTR_SUPPORTED_FEATURES as ATTR_SUPPORTED_FEATURES, CONF_ENTITIES as CONF_ENTITIES, CONF_NAME as CONF_NAME, CONF_UNIQUE_ID as CONF_UNIQUE_ID, SERVICE_MEDIA_NEXT_TRACK as SERVICE_MEDIA_NEXT_TRACK, SERVICE_MEDIA_PAUSE as SERVICE_MEDIA_PAUSE, SERVICE_MEDIA_PLAY as SERVICE_MEDIA_PLAY, SERVICE_MEDIA_PREVIOUS_TRACK as SERVICE_MEDIA_PREVIOUS_TRACK, SERVICE_MEDIA_SEEK as SERVICE_MEDIA_SEEK, SERVICE_MEDIA_STOP as SERVICE_MEDIA_STOP, SERVICE_SHUFFLE_SET as SERVICE_SHUFFLE_SET, SERVICE_TURN_OFF as SERVICE_TURN_OFF, SERVICE_TURN_ON as SERVICE_TURN_ON, SERVICE_VOLUME_MUTE as SERVICE_VOLUME_MUTE, SERVICE_VOLUME_SET as SERVICE_VOLUME_SET, STATE_UNAVAILABLE as STATE_UNAVAILABLE, STATE_UNKNOWN as STATE_UNKNOWN
from homeassistant.core import CALLBACK_TYPE as CALLBACK_TYPE, Event as Event, HomeAssistant as HomeAssistant, State as State, callback as callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback as AddEntitiesCallback
from homeassistant.helpers.event import EventStateChangedData as EventStateChangedData, async_track_state_change_event as async_track_state_change_event
from homeassistant.helpers.typing import ConfigType as ConfigType, DiscoveryInfoType as DiscoveryInfoType
from typing import Any

KEY_ANNOUNCE: str
KEY_CLEAR_PLAYLIST: str
KEY_ENQUEUE: str
KEY_ON_OFF: str
KEY_PAUSE_PLAY_STOP: str
KEY_PLAY_MEDIA: str
KEY_SHUFFLE: str
KEY_SEEK: str
KEY_TRACKS: str
KEY_VOLUME: str
DEFAULT_NAME: str

async def async_setup_platform(hass: HomeAssistant, config: ConfigType, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None) -> None: ...
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None: ...
def async_create_preview_media_player(hass: HomeAssistant, name: str, validated_config: dict[str, Any]) -> MediaPlayerGroup: ...

class MediaPlayerGroup(MediaPlayerEntity):
    _unrecorded_attributes: Incomplete
    _attr_available: bool
    _attr_should_poll: bool
    _name: Incomplete
    _attr_unique_id: Incomplete
    _entities: Incomplete
    _features: Incomplete
    def __init__(self, unique_id: str | None, name: str, entities: list[str]) -> None: ...
    def async_on_state_change(self, event: Event[EventStateChangedData]) -> None: ...
    def async_update_supported_features(self, entity_id: str, new_state: State | None) -> None: ...
    def async_start_preview(self, preview_callback: Callable[[str, Mapping[str, Any]], None]) -> CALLBACK_TYPE: ...
    async def async_added_to_hass(self) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def extra_state_attributes(self) -> Mapping[str, Any]: ...
    async def async_clear_playlist(self) -> None: ...
    async def async_media_next_track(self) -> None: ...
    async def async_media_pause(self) -> None: ...
    async def async_media_play(self) -> None: ...
    async def async_media_previous_track(self) -> None: ...
    async def async_media_seek(self, position: float) -> None: ...
    async def async_media_stop(self) -> None: ...
    async def async_mute_volume(self, mute: bool) -> None: ...
    async def async_play_media(self, media_type: MediaType | str, media_id: str, **kwargs: Any) -> None: ...
    async def async_set_shuffle(self, shuffle: bool) -> None: ...
    async def async_turn_on(self) -> None: ...
    async def async_set_volume_level(self, volume: float) -> None: ...
    async def async_turn_off(self) -> None: ...
    async def async_volume_up(self) -> None: ...
    async def async_volume_down(self) -> None: ...
    _attr_state: Incomplete
    _attr_supported_features: Incomplete
    def async_update_group_state(self) -> None: ...
