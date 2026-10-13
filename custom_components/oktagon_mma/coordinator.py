"""Fetch and coordinate OKTAGON event overview data."""
from datetime import timedelta
import logging

from aiohttp import ClientError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .events import EVENTS_URL, OktagonEvent, parse_events
from .fightcard import Bout, find_event_page_url, parse_embedded_fight_card

_LOGGER = logging.getLogger(__name__)


class OktagonCoordinator(DataUpdateCoordinator[list[OktagonEvent]]):
    """Refresh the event overview every six hours."""

    def __init__(self, hass):
        self.fight_card: list[Bout] = []
        self.fight_card_url: str | None = None
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
        # The fight card is optional. A missing/changed event detail page must
        # never take down the existing calendar or event sensors.
        self.fight_card = []
        self.fight_card_url = find_event_page_url(html, events[0].title)
        if events[0].title.upper().startswith('OKTAGON '):
            import re
            match = re.match(r'^OKTAGON ([0-9]+)\\b', events[0].title, re.I)
            if match:
                number = match.group(1)
                # The overview contains the official slug as part of its Next.js data.
                slug_match = re.search(r'(?<![a-z0-9])oktagon-' + number + r'-[a-z0-9-]+', html, re.I)
                if slug_match:
                    self.fight_card_url = 'https://oktagonmma.com/de/events/' + slug_match.group(0) + '/'
        if self.fight_card_url:
            try:
                async with session.get(self.fight_card_url, timeout=20) as detail_response:
                    detail_response.raise_for_status()
                    detail_html = await detail_response.text()
                self.fight_card = parse_embedded_fight_card(detail_html)
            except (ClientError, TimeoutError) as err:
                _LOGGER.warning("Fight card temporarily unavailable: %s", err)
        return events
