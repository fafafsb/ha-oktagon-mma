"""Sensors for the next OKTAGON MMA event."""
from datetime import date

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class NextEventSensor(CoordinatorEntity, SensorEntity):
    """Name and metadata of the next event."""

    _attr_name = "Next OKTAGON event"
    _attr_icon = "mdi:boxing-glove"
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next_event"

    @property
    def native_value(self):
        events = self.coordinator.data or []
        return events[0].title if events else None

    @property
    def extra_state_attributes(self):
        events = self.coordinator.data or []
        if not events:
            return {}
        event = events[0]
        return {
            "date": event.day.isoformat(),
            "location": event.venue,
            "days_until": (event.day - date.today()).days,
        }


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NextEventSensor(coordinator, entry)])
