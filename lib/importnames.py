"""Load the read-only TOML configuration once during application startup."""

import logging

from lib import StateManager

loaded_config = StateManager.load_config()
names = loaded_config.get("names", {}) if isinstance(loaded_config, dict) else {}
if not isinstance(names, dict):
    names = {}
    logging.getLogger(__name__).error("Configuration names must be a TOML table")

__all__ = ["names", "loaded_config"]
