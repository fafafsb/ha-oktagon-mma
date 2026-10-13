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
