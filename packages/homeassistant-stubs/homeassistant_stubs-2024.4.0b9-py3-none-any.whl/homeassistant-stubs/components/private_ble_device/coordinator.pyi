from .const import DOMAIN as DOMAIN
from _typeshed import Incomplete
from collections.abc import Callable
from cryptography.hazmat.primitives.ciphers import Cipher as Cipher
from homeassistant.components import bluetooth as bluetooth
from homeassistant.components.bluetooth.match import BluetoothCallbackMatcher as BluetoothCallbackMatcher
from homeassistant.core import HomeAssistant as HomeAssistant

_LOGGER: Incomplete
UnavailableCallback: Incomplete
Cancellable = Callable[[], None]

def async_last_service_info(hass: HomeAssistant, irk: bytes) -> bluetooth.BluetoothServiceInfoBleak | None: ...

class PrivateDevicesCoordinator:
    hass: Incomplete
    _irks: Incomplete
    _unavailable_callbacks: Incomplete
    _service_info_callbacks: Incomplete
    _mac_to_irk: Incomplete
    _irk_to_mac: Incomplete
    _ignored: Incomplete
    _unavailability_trackers: Incomplete
    _listener_cancel: Incomplete
    def __init__(self, hass: HomeAssistant) -> None: ...
    def _async_ensure_started(self) -> None: ...
    def _async_ensure_stopped(self) -> None: ...
    def _async_track_unavailable(self, service_info: bluetooth.BluetoothServiceInfoBleak) -> None: ...
    def _async_irk_resolved_to_mac(self, irk: bytes, mac: str) -> None: ...
    def _async_track_service_info(self, service_info: bluetooth.BluetoothServiceInfoBleak, change: bluetooth.BluetoothChange) -> None: ...
    def _async_maybe_learn_irk(self, irk: bytes) -> None: ...
    def _async_maybe_forget_irk(self, irk: bytes) -> None: ...
    def async_track_service_info(self, callback: bluetooth.BluetoothCallback, irk: bytes) -> Cancellable: ...
    def async_track_unavailable(self, callback: UnavailableCallback, irk: bytes) -> Cancellable: ...

def async_get_coordinator(hass: HomeAssistant) -> PrivateDevicesCoordinator: ...
