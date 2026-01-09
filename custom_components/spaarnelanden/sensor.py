from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        SpaarnelandenContainerSensor(coordinator, container_id)
        for container_id in coordinator.container_ids
    )


class SpaarnelandenContainerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, container_id):
        super().__init__(coordinator)
        self.container_id = container_id
        self._attr_unique_id = f"spaarnelanden_{container_id}"
        self._attr_name = f"Spaarnelanden Container {container_id}"
        self._attr_native_unit_of_measurement = "%"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self.container_id)
        return data.get("dFillingDegree") if data else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self.container_id)
        if not data:
            return {}

        return {
            "latitude": data.get("dLatitude"),
            "longitude": data.get("dLongitude"),
            "last_emptied": data.get("sDateLastEmptied"),
            "type": data.get("sProductName"),
            "registration_number": data.get("sRegistrationNumber"),
        }
