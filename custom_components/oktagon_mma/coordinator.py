"""Fetch and coordinate OKTAGON event overview data."""
from datetime import timedelta
import logging

from aiohttp import ClientError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .events import EVENTS_URL, OktagonEvent, parse_events

_LOGGER = logging.getLogger(__name__)


class OktagonCoordinator(DataUpdateCoordinator[list[OktagonEvent]]):
    """Refresh the event overview every six hours."""

    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="OKTAGON MMA",
            update_interval=timedelta(hours=6),
        )

    async def _async_update_data(self) -> list[OktagonEvent]:
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(EVENTS_URL, timeout=20) as response:
                response.raise_for_status()
                html = await response.text()
        except (ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Unable to fetch OKTAGON events: {err}") from err

        events = parse_events(html)
        if not events:
            # Never silently present a parsing failure as "no upcoming events".
            raise UpdateFailed("No events parsed; source format may have changed")
        return events
