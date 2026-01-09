from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "spaarnelanden"

URL = "https://inzameling.spaarnelanden.nl/"

# Config keys
CONF_CONTAINERS = "containers"

# Platforms
PLATFORMS: list[Platform] = [Platform.SENSOR]
