"""ParseDoc Filesystem utilities"""

import os
import tempfile
from pathlib import Path


def validate_input_path(input_path: str) -> bool:
    """Validate that input path exists and is a readable file."""
    try:
        path = Path(input_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def ensure_dir(path: str) -> str:
    """Create directory if it does not exist and return its path."""
    os.makedirs(path, exist_ok=True)
    return path


def create_temp_dir(prefix: str = "parsedoc_") -> str:
    """Create a temporary directory for processing."""
    return tempfile.mkdtemp(prefix=prefix)


def default_config_path() -> str:
    """Return the default config file path."""
    return os.path.expanduser("~/.config/parsedoc/config.toml")


def default_cache_dir() -> str:
    """Return the default cache directory."""
    return os.path.expanduser("~/.cache/parsedoc/")
