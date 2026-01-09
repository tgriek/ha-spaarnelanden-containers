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

_ID_DIGITS_RE = re.compile(r"\d+")


def _normalize_numeric_id(value: Any) -> str | None:
    """Normalize numeric IDs like iId to a stable string representation."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value)

    s = str(value).strip()
    if not s:
        return None
    try:
        f = float(s)
        return str(int(f)) if f.is_integer() else s
    except Exception:
        pass

    m = _ID_DIGITS_RE.search(s)
    return m.group(0) if m else None


def _normalize_identifier(value: Any) -> str | None:
    """Normalize user-entered identifiers / registration numbers."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None

    s = str(value).strip()
    if not s:
        return None

    # If someone entered "20126.0" we treat it as 20126, but keep leading zeros otherwise.
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
    except Exception:
        pass

    return s


class SpaarnelandenCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        container_ids: list[str],
        update_interval=None,
    ) -> None:
        # Historically we called these "container IDs", but in practice users enter the
        # registration number ("sRegistrationNumber") from the website.
        self.container_ids = {cid for c in container_ids if (cid := _normalize_identifier(c))}
        self._numeric_container_ids = {cid for c in container_ids if (cid := _normalize_numeric_id(c))}
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

        all_numeric_ids = {cid for c in containers if (cid := _normalize_numeric_id(c.get("iId")))}
        all_registration_numbers = {
            cid for c in containers if (cid := _normalize_identifier(c.get("sRegistrationNumber")))
        }

        filtered: dict[str, Any] = {}
        for c in containers:
            reg = _normalize_identifier(c.get("sRegistrationNumber"))
            if reg and reg in self.container_ids:
                filtered[reg] = c
                continue

            numeric_id = _normalize_numeric_id(c.get("iId"))
            if numeric_id and numeric_id in self._numeric_container_ids:
                filtered[numeric_id] = c

        if not filtered:
            _LOGGER.warning(
                "No Spaarnelanden containers matched configured identifiers. configured=%s "
                "available_reg(sample)=%s total_reg=%s available_iId(sample)=%s total_iId=%s",
                sorted(self.container_ids),
                sorted(list(all_registration_numbers))[:20],
                len(all_registration_numbers),
                sorted(list(all_numeric_ids))[:20],
                len(all_numeric_ids),
            )
        else:
            _LOGGER.debug(
                "Fetched Spaarnelanden containers: matched=%s configured=%s total_reg=%s total_iId=%s",
                len(filtered),
                len(self.container_ids),
                len(all_registration_numbers),
                len(all_numeric_ids),
            )
        return filtered
