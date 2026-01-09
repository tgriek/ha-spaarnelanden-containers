import re
import json
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .const import URL

_LOGGER = logging.getLogger(__name__)

class SpaarnelandenCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, container_ids, update_interval=None):
        self.container_ids = set(container_ids)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_update_data,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        session = async_get_clientsession(self.hass)
        async with session.get(URL) as response:
            html = await response.text()

        match = re.search(
            r"var oContainerModel\s*=\s*(\[[\s\S]*?\]);",
            html,
        )

        if not match:
            raise ValueError("oContainerModel not found")

        containers = json.loads(match.group(1))

        return {
            str(c["iId"]): c
            for c in containers
            if str(c.get("iId")) in self.container_ids
        }
