"""Experimental fight-card parser for structured event-page data.

Only confirmed bouts are returned. This module is deliberately not wired into
Home Assistant until an official event page has been verified against it.
"""
from dataclasses import dataclass
from html.parser import HTMLParser
import json


@dataclass(frozen=True)
class Bout:
    fighter_one: str
    fighter_two: str
    weight_class: str | None = None


class _JsonLd(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self._collect = False
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type", "").lower() == "application/ld+json":
            self._collect = True
            self._parts = []

    def handle_data(self, data):
        if self._collect:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._collect:
            self.blocks.append("".join(self._parts))
            self._collect = False


def _objects(value):
    if isinstance(value, list):
        for item in value:
            yield from _objects(item)
    elif isinstance(value, dict):
        yield value
        if "@graph" in value:
            yield from _objects(value["@graph"])


def _name(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(value.get("name") or "").strip()
    return ""


def parse_fight_card(html: str) -> list[Bout]:
    """Extract bouts only when structured data explicitly names two opponents.

    An event headline such as 'Fighter A vs Fighter B' is not sufficient
    evidence of a complete fight card.
    """
    parser = _JsonLd()
    parser.feed(html)
    bouts = []
    seen = set()
    for block in parser.blocks:
        try:
            data = json.loads(block)
        except (ValueError, TypeError):
            continue
        for item in _objects(data):
            types = item.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if not any(t in ("SportsEvent", "Event") for t in types):
                continue
            competitors = item.get("competitor", [])
            if not isinstance(competitors, list) or len(competitors) != 2:
                continue
            names = [_name(c) for c in competitors]
            if not all(names) or names[0] == names[1]:
                continue
            key = tuple(names)
            if key not in seen:
                seen.add(key)
                bouts.append(Bout(*names))
    return bouts


class _VisibleText(HTMLParser):
    """Flatten rendered text while skipping scripts and styles."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        elif tag in ("h1", "h2", "h3", "h4", "h5", "p", "div", "section", "br", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "p", "div", "section", "li"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def parse_visible_fight_card(html: str) -> list[Bout]:
    """Parse a clearly labelled main-card section of an OKTAGON event page.

    The official page renders pairs as 'Name / VS / Name'. Never guess a
    missing opponent or derive a card from promotional headlines.
    """
    import re

    parser = _VisibleText()
    parser.feed(html)
    lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(parser.parts).splitlines()]
    lines = [line for line in lines if line]
    try:
        start = next(i for i, value in enumerate(lines) if value.upper() == "MAIN CARD")
    except StopIteration:
        return []
    section = lines[start + 1:]
    for i, value in enumerate(section):
        if value.upper() in ("PRELIMS", "PRELIMINARY CARD", "NEWS", "EVENT DETAIL"):
            section = section[:i]
            break
    weights = {
        "middleweight", "light heavyweight", "flyweight", "featherweight",
        "lightweight", "welterweight", "heavyweight", "bantamweight",
        "strawweight", "catchweight",
    }
    bouts = []
    seen = set()
    for i, line in enumerate(section):
        if line.upper() != "VS" or i == 0 or i + 1 >= len(section):
            continue
        first, second = section[i - 1], section[i + 1]
        if any(not name or name.upper() == "TBA" or len(name) > 80 for name in (first, second)):
            continue
        if not all(re.search(r"[A-Za-zÀ-ž]", name) for name in (first, second)):
            continue
        if first == second or (first, second) in seen:
            continue
        weight = next(
            (value for value in reversed(section[max(0, i - 7):i - 1])
             if value.lower() in weights),
            None,
        )
        seen.add((first, second))
        bouts.append(Bout(first, second, weight))
    return bouts


def find_event_page_url(html: str, event_title: str) -> str | None:
    """Find a matching official event detail URL without guessing the slug."""
    import re
    from html import unescape
    from urllib.parse import urljoin, urlparse

    match = re.match(r"^OKTAGON ([0-9]+)\\b", event_title, re.I)
    if not match:
        return None
    number = match.group(1)
    for href in re.findall(r"""href\\s*=\\s*["']([^"']+)["']""", html, re.I):
        url = urljoin("https://oktagonmma.com/", unescape(href))
        parsed = urlparse(url)
        pattern = rf"^/(?:en/)?events/oktagon-{number}(?:-|/)"
        if parsed.scheme == "https" and parsed.hostname == "oktagonmma.com" and re.match(pattern, parsed.path):
            return url
    return None
