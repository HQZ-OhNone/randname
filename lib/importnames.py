"""Load the read-only TOML configuration once during application startup."""

import logging

from lib import StateManager


def _names_for(rosters: dict, key: str) -> dict:
    """Return the usable ``names`` table for *key*, falling back to one student."""
    names = rosters.get(key, {}).get("names", {}) if isinstance(rosters, dict) else {}
    if not isinstance(names, dict) or not names:
        logging.getLogger(__name__).error("No usable roster was loaded")
        return {"0": "Student 1"}
    return names


loaded_config = StateManager.load_config()
rosters, ROSTER_FALLBACK_USED = StateManager.load_rosters()
app_config = loaded_config.get("app", {})
if not isinstance(app_config, dict):
    app_config = {}
configured_roster = app_config.get("roster", "class_1")
if not isinstance(configured_roster, str) or configured_roster not in rosters:
    configured_roster = next(iter(rosters), "class_1")
active_roster = configured_roster
names = _names_for(rosters, active_roster)


def select_roster(name: str) -> dict:
    global active_roster, names
    roster = rosters.get(name)
    if not isinstance(roster, dict) or not isinstance(roster.get("names"), dict):
        return names
    active_roster = name
    names = roster["names"]
    return names


def reload_data() -> None:
    global loaded_config, rosters, active_roster, names, ROSTER_FALLBACK_USED
    loaded_config = StateManager.load_config()
    rosters, ROSTER_FALLBACK_USED = StateManager.load_rosters()
    app_config = loaded_config.get("app", {})
    if not isinstance(app_config, dict):
        app_config = {}
    configured_roster = app_config.get("roster", "class_1")
    active_roster = configured_roster if configured_roster in rosters else next(iter(rosters), "class_1")
    # Mirror the import time fallback: an empty or malformed ``names`` table must
    # not leave the program without anybody to draw.
    names = _names_for(rosters, active_roster)

__all__ = [
    "names",
    "loaded_config",
    "rosters",
    "active_roster",
    "ROSTER_FALLBACK_USED",
    "select_roster",
    "reload_data",
]
