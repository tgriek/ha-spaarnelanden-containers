from __future__ import annotations

import re
import json
import logging
from typing import Any

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .const import URL

_LOGGER = logging.getLogger(__name__)

class SpaarnelandenCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        container_ids: list[str],
        update_interval=None,
    ) -> None:
        self.container_ids = {str(c) for c in container_ids}
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_update_data,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(20):
                async with session.get(URL) as response:
                    response.raise_for_status()
                    html = await response.text()
        except Exception as err:
            raise UpdateFailed(f"Error fetching Spaarnelanden data: {err}") from err

        match = re.search(
            r"var oContainerModel\s*=\s*(\[[\s\S]*?\]);",
            html,
        )

        if not match:
            raise UpdateFailed("Spaarnelanden page format changed: oContainerModel not found")

        try:
            containers = json.loads(match.group(1))
        except json.JSONDecodeError as err:
            raise UpdateFailed(f"Failed to parse Spaarnelanden container JSON: {err}") from err

        return {
            str(c["iId"]): c
            for c in containers
            if str(c.get("iId")) in self.container_ids
        }
