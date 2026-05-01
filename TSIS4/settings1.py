"""settings_manager.py — load/save settings.json."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULTS = {
    "snake_color": [60, 210, 80],
    "grid":        False,
    "sound":       False,
}


def load() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        _write(DEFAULTS.copy())
        return DEFAULTS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = DEFAULTS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULTS.copy()


def save(settings: dict):
    _write(settings)


def _write(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)