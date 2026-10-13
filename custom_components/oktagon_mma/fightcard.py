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
    fighter_one_image: str | None = None
    fighter_two_image: str | None = None


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
        bouts.append(Bout(first, second, weight, fighter_image(left), fighter_image(right)))
    return bouts


def find_event_page_url(html: str, event_title: str) -> str | None:
    """Find an event link explicitly present in the official overview.

    Prefer a detail page on oktagonmma.com, otherwise accept the event page
    on oktagon.tv linked by the official OKTAGON website.
    """
    import re
    from html import unescape
    from urllib.parse import urljoin, urlparse

    match = re.match(r"^OKTAGON ([0-9]+)\b", event_title, re.I)
    if not match:
        return None
    number = match.group(1)
    links = re.findall(r"""href\s*=\s*["']([^"']+)["']""", html, re.I)
    candidates = []
    for href in links:
        url = urljoin("https://oktagonmma.com/", unescape(href))
        parsed = urlparse(url)
        if parsed.scheme != "https":
            continue
        if parsed.hostname in ("oktagonmma.com", "www.oktagonmma.com"):
            if re.search(rf"/(?:en/|de/|cs/|pl/)?events/oktagon-{number}(?:-|/|$)", parsed.path, re.I):
                candidates.append((0, url))
        elif parsed.hostname == "oktagon.tv":
            if re.fullmatch(rf"/event/oktagon-{number}/?", parsed.path, re.I):
                candidates.append((1, url))
    return min(candidates)[1] if candidates else None


class _NextData(HTMLParser):
    """Read Next.js server-side JSON without executing scripts."""

    def __init__(self):
        super().__init__()
        self.collect = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "__NEXT_DATA__":
            self.collect = True

    def handle_data(self, data):
        if self.collect:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.collect = False


def parse_embedded_fight_card(html: str) -> list[Bout]:
    """Extract explicit fighter pairs from the official Next.js event payload."""
    parser = _NextData()
    parser.feed(html)
    if not parser.parts:
        return []
    try:
        payload = json.loads("".join(parser.parts))
    except (ValueError, TypeError):
        return []
    bouts = []
    seen = set()

    def fighter_image(fighter):
        """Prefer official fight-card art, falling back to a profile portrait."""
        from urllib.parse import urlparse

        for field in ("imageFightCard", "imageProfile"):
            image = fighter.get(field)
            if not isinstance(image, dict):
                continue
            urls = image.get("url")
            if not isinstance(urls, dict):
                continue
            for key in ("en", "cs", "de", "pl"):
                url = urls.get(key)
                if not isinstance(url, str):
                    continue
                parsed = urlparse(url)
                if parsed.scheme == "https" and parsed.hostname == "assets.oktagonmma.com":
                    return url
        return None

    def visit(value):
        if isinstance(value, dict):
            fights = value.get("fights")
            if isinstance(fights, list):
                for fight in fights:
                    if not isinstance(fight, dict):
                        continue
                    left, right = fight.get("fighter1"), fight.get("fighter2")
                    if not isinstance(left, dict) or not isinstance(right, dict):
                        continue
                    def fighter_name(fighter):
                        return " ".join(str(fighter.get(k) or "").strip()
                                        for k in ("firstName", "lastName")).strip()
                    first, second = fighter_name(left), fighter_name(right)
                    if not first or not second or first == second:
                        continue
                    key = (first, second)
                    if key not in seen:
                        seen.add(key)
                        weight = fight.get("weightClass")
                        if isinstance(weight, dict):
                            weight = weight.get("title") or weight.get("name")
                        if not isinstance(weight, str):
                            weight = None
                        bouts.append(Bout(first, second, weight))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload.get("props", {}).get("pageProps", {}))
    return bouts
