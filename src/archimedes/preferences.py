"""Persistent user preferences for Archimedes (first-run onboarding, etc.)."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".archimedes"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _load_config() -> dict:
    """Read config from disk; return empty dict on missing or invalid file."""
    if not CONFIG_FILE.is_file():
        return {}
    try:
        with CONFIG_FILE.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_config(data: dict) -> bool:
    """Write config to disk. Returns True on success."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        return True
    except OSError:
        return False


def is_welcome_dismissed() -> bool:
    """Return True if the user has dismissed the welcome screen."""
    return bool(_load_config().get("welcome_dismissed", False))


def set_welcome_dismissed(dismissed: bool = True) -> None:
    """Persist whether the welcome screen should be shown on launch."""
    data = _load_config()
    data["welcome_dismissed"] = dismissed
    _save_config(data)
