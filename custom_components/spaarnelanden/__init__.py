from datetime import timedelta
from .const import DOMAIN
from .coordinator import SpaarnelandenCoordinator

async def async_setup_entry(hass, entry):
    coordinator = SpaarnelandenCoordinator(
        hass,
        entry.data["containers"],
        update_interval=timedelta(hours=2),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass, entry):
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
