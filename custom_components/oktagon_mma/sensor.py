"""Sensors for upcoming OKTAGON MMA events."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .events import EVENTS_URL


class OktagonSensor(CoordinatorEntity, SensorEntity):
    """Shared coordinator-backed sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, suffix: str):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{suffix}"

    @property
    def next_event(self):
        events = self.coordinator.data or []
        return events[0] if events else None


class NextEventSensor(OktagonSensor):
    """Next event title and its metadata."""

    _attr_name = "Next OKTAGON event"
    _attr_icon = "mdi:boxing-glove"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "next_event")

    @property
    def native_value(self):
        event = self.next_event
        return event.title if event else None

    @property
    def extra_state_attributes(self):
        event = self.next_event
        if event is None:
            return {}
        return {
            "date": event.day.isoformat(),
            "location": event.venue,
            "days_until": (event.day - dt_util.now().date()).days,
            "events_url": EVENTS_URL,
        }


class CountdownSensor(OktagonSensor):
    """Whole calendar days until the next event."""

    _attr_name = "Days until next OKTAGON"
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = "d"

    async def async_added_to_hass(self):
        """Update countdown at local midnight, even without a data refresh."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_time_change(
                self.hass,
                self._handle_midnight,
                hour=0,
                minute=0,
                second=0,
            )
        )

    def _handle_midnight(self, now):
        """Refresh the displayed number of days at midnight."""
        self.async_write_ha_state()

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "countdown")

    @property
    def native_value(self):
        event = self.next_event
        return max(0, (event.day - dt_util.now().date()).days) if event else None


class EventDateSensor(OktagonSensor):
    """Date of the next event."""

    _attr_name = "Next OKTAGON date"
    _attr_icon = "mdi:calendar"
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "event_date")

    @property
    def native_value(self):
        event = self.next_event
        return event.day if event else None


class EventLocationSensor(OktagonSensor):
    """Venue of the next event."""

    _attr_name = "Next OKTAGON location"
    _attr_icon = "mdi:map-marker"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "event_location")

    @property
    def native_value(self):
        event = self.next_event
        return event.venue if event else None


class FightCardSensor(OktagonSensor):
    """Number of confirmed matchups for the next event."""

    _attr_name = "Next OKTAGON fight card"
    _attr_icon = "mdi:boxing-glove"
    _attr_native_unit_of_measurement = "fights"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "fight_card")

    @property
    def native_value(self):
        return len(self.coordinator.fight_card) if self.coordinator.fight_card_url else None

    @property
    def extra_state_attributes(self):
        return {
            "event": self.next_event.title if self.next_event else None,
            "event_url": self.coordinator.fight_card_url,
            "fights": [
                {
                    "fighter_one": bout.fighter_one,
                    "fighter_two": bout.fighter_two,
                    "weight_class": bout.weight_class,
                    "fighter_one_image": bout.fighter_one_image,
                    "fighter_two_image": bout.fighter_two_image,
                    "main_event": index == 0,
                }
                for index, bout in enumerate(self.coordinator.fight_card)
            ],
        }


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensors from the shared coordinator."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            NextEventSensor(coordinator, entry),
            CountdownSensor(coordinator, entry),
            EventDateSensor(coordinator, entry),
            EventLocationSensor(coordinator, entry),
            FightCardSensor(coordinator, entry),
        ]
    )
