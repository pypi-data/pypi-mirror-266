from _typeshed import Incomplete
from homeassistant.exceptions import HomeAssistantError as HomeAssistantError

_LOGGER: Incomplete

class WriteError(HomeAssistantError): ...

def write_utf8_file_atomic(filename: str, utf8_data: bytes | str, private: bool = False, mode: str = 'w') -> None: ...
def write_utf8_file(filename: str, utf8_data: bytes | str, private: bool = False, mode: str = 'w') -> None: ...
