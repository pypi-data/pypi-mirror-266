from . import ATTR_MAXIMUM as ATTR_MAXIMUM, ATTR_MINIMUM as ATTR_MINIMUM, ATTR_STEP as ATTR_STEP, DOMAIN as DOMAIN, SERVICE_SET_VALUE as SERVICE_SET_VALUE, VALUE as VALUE
from _typeshed import Incomplete
from collections.abc import Iterable
from homeassistant.const import ATTR_ENTITY_ID as ATTR_ENTITY_ID
from homeassistant.core import Context as Context, HomeAssistant as HomeAssistant, State as State
from typing import Any

_LOGGER: Incomplete

async def _async_reproduce_state(hass: HomeAssistant, state: State, *, context: Context | None = None, reproduce_options: dict[str, Any] | None = None) -> None: ...
async def async_reproduce_states(hass: HomeAssistant, states: Iterable[State], *, context: Context | None = None, reproduce_options: dict[str, Any] | None = None) -> None: ...
