"""Read-only parser for the public OKTAGON events overview.

This is an experimental source adapter, not an official OKTAGON API.
Dates from the overview have no verified start time, so events are all-day.
"""

from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
import re

EVENTS_URL = "https://oktagonmma.com/en/events/"
_DATE = re.compile(r"(?<!\d)(\d{2})\.(\d{2})\.(\d{4})(?!\d)")


@dataclass(frozen=True)
class OktagonEvent:
    """One upcoming event from the public overview."""

    title: str
    day: date
    venue: str


class _OverviewText(HTMLParser):
    """Extract visible text, ignoring script/style blocks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._hidden += 1
        elif tag in ("h1", "h2", "h3", "p", "div", "article", "br"):
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._hidden = max(0, self._hidden - 1)
        elif tag in ("h1", "h2", "h3", "p", "div", "article"):
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._hidden:
            self.parts.append(data)


def parse_events(html: str, today: date | None = None) -> list[OktagonEvent]:
    """Parse overview text conservatively; ignore entries without a full date.

    NOTE: This heuristic requires testing against the real site HTML before
    it can be used as a Home Assistant data source.
    """
    parser = _OverviewText()
    parser.feed(html)
    lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(parser.parts).splitlines()]
    lines = [line for line in lines if line]
    cutoff = today or date.today()
    events: list[OktagonEvent] = []
    seen: set[tuple[str, date]] = set()

    for index, title in enumerate(lines):
        if not re.match(r"^(?:OKTAGON (?:\\d+\\b|INFINITY\\b)|TIPSPORT CAGE GAME\\b)", title, re.I):
            continue
        if len(title) > 120 or _DATE.search(title):
            continue
        for detail in lines[index + 1:index + 5]:
            match = _DATE.search(detail)
            if not match:
                continue
            try:
                day = date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            except ValueError:
                break
            if day < cutoff:
                break
            venue = detail[match.end():].strip(" ,-–")
            if not venue:
                break
            key = (title, day)
            if key not in seen:
                events.append(OktagonEvent(title=title, day=day, venue=venue))
                seen.add(key)
            break

    return sorted(events, key=lambda event: (event.day, event.title))
