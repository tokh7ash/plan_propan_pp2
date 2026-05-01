"""persistence.py — save / load leaderboard and settings."""
import json
import os

LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")
SETTINGS_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   "blue",   # blue | red | green
    "difficulty":  "normal", # easy | normal | hard
}


# ── Leaderboard ──────────────────────────────────────────────────────────────

def load_leaderboard():
    """Return list of up-to-10 score dicts, sorted best-first."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[:10]
    except (json.JSONDecodeError, KeyError):
        return []


def save_score(name: str, score: int, distance: int, coins: int):
    """Append a new entry and keep only the top 10."""
    board = load_leaderboard()
    board.append({"name": name, "score": score, "distance": distance, "coins": coins})
    board.sort(key=lambda x: x["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)
    return board


# ── Settings ─────────────────────────────────────────────────────────────────

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        _write_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Fill any missing keys with defaults
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except (json.JSONDecodeError, KeyError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    _write_settings(settings)


def _write_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
