import re
import json
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import URL

class SpaarnelandenCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, container_ids, *args, **kwargs):
        self.container_ids = set(container_ids)
        super().__init__(hass, *args, **kwargs)

    async def _async_update_data(self):
        async with aiohttp.ClientSession() as session:
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
