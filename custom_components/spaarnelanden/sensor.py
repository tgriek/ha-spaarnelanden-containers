from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SpaarnelandenCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SpaarnelandenCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [SpaarnelandenContainerSensor(coordinator, container_id) for container_id in coordinator.container_ids]
    )


class SpaarnelandenContainerSensor(CoordinatorEntity[SpaarnelandenCoordinator], SensorEntity):
    def __init__(self, coordinator: SpaarnelandenCoordinator, container_id: str) -> None:
        super().__init__(coordinator)
        self.container_id = container_id
        self._attr_unique_id = f"spaarnelanden_{container_id}"
        self._attr_name = f"Spaarnelanden Container {container_id}"
        self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self) -> Any:
        data = self.coordinator.data.get(self.container_id)
        return data.get("dFillingDegree") if data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
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

    @property
    def device_info(self) -> DeviceInfo:
        data = self.coordinator.data.get(self.container_id) or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self.container_id)},
            name=f"Spaarnelanden Container {self.container_id}",
            manufacturer="Spaarnelanden",
            model=data.get("sProductName") or "Container",
        )
