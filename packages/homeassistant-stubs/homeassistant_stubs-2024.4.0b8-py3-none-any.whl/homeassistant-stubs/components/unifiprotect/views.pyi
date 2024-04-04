from .const import DOMAIN as DOMAIN
from .data import ProtectData as ProtectData
from _typeshed import Incomplete
from aiohttp import web
from homeassistant.components.http import HomeAssistantView as HomeAssistantView
from homeassistant.core import HomeAssistant as HomeAssistant, callback as callback
from http import HTTPStatus
from pyunifiprotect.data import Camera, Event as Event
from typing import Any

_LOGGER: Incomplete

def async_generate_thumbnail_url(event_id: str, nvr_id: str, width: int | None = None, height: int | None = None) -> str: ...
def async_generate_event_video_url(event: Event) -> str: ...
def _client_error(message: Any, code: HTTPStatus) -> web.Response: ...
def _400(message: Any) -> web.Response: ...
def _403(message: Any) -> web.Response: ...
def _404(message: Any) -> web.Response: ...
def _validate_event(event: Event) -> None: ...

class ProtectProxyView(HomeAssistantView):
    requires_auth: bool
    hass: Incomplete
    data: Incomplete
    def __init__(self, hass: HomeAssistant) -> None: ...
    def _get_data_or_404(self, nvr_id: str) -> ProtectData | web.Response: ...

class ThumbnailProxyView(ProtectProxyView):
    url: str
    name: str
    async def get(self, request: web.Request, nvr_id: str, event_id: str) -> web.Response: ...

class VideoProxyView(ProtectProxyView):
    url: str
    name: str
    def _async_get_camera(self, data: ProtectData, camera_id: str) -> Camera | None: ...
    async def get(self, request: web.Request, nvr_id: str, camera_id: str, start: str, end: str) -> web.StreamResponse: ...
