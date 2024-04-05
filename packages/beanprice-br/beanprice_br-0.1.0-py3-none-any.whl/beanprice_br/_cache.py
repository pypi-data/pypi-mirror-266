import os
import platform
from pathlib import Path


def _get_path_from_env(key: str) -> Path | None:
    value = os.environ.get(key)
    if value is None or value == "":
        return None
    return Path(value)


match platform.system():
    case "Linux":
        CACHE_BASE_PATH = _get_path_from_env("XDG_CACHE_HOME") or Path.home() / ".cache"
    case "Darwin":
        CACHE_BASE_PATH = Path.home() / "Library" / "Caches"
    case "Windows":
        CACHE_BASE_PATH = (
            _get_path_from_env("LOCALAPPDATA") or Path.home() / "AppData" / "Local"
        )
    case _:
        CACHE_BASE_PATH = Path.home() / ".cache"

CACHE_BASE_PATH.mkdir(parents=True, exist_ok=True)
