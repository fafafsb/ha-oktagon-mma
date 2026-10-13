"""Upcoming OKTAGON MMA events calendar."""
from datetime import timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class OktagonCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar of upcoming events."""

    _attr_name = "OKTAGON MMA Events"
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_events"

    @staticmethod
    def _event(event):
        return CalendarEvent(
            summary=event.title,
            start=event.day,
            end=event.day + timedelta(days=1),
            location=event.venue,
        )

    @property
    def event(self):
        events = self.coordinator.data or []
        return self._event(events[0]) if events else None

    async def async_get_events(self, hass, start_date, end_date):
        return [
            self._event(event)
            for event in (self.coordinator.data or [])
            if start_date.date() <= event.day < end_date.date()
        ]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OktagonCalendar(coordinator, entry)])
