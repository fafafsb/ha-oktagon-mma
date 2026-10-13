"""Tests for the experimental OKTAGON overview parser."""

from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components" / "oktagon_mma"))
from events import parse_events  # noqa: E402


def test_upcoming_events_are_sorted_and_deduplicated():
    html = """
    <h2>OKTAGON 96: GOGOLADZE VS. KLINKHAMMER</h2>
    <p>31.10.2026 SAP Garden, München</p>
    <h2>OKTAGON 95: KINCL VS. HUMBURGER</h2>
    <p>17.10.2026 Mattoni Arena, Karlovy Vary</p>
    <h2>OKTAGON 95: KINCL VS. HUMBURGER</h2>
    <p>17.10.2026 Mattoni Arena, Karlovy Vary</p>
    """
    result = parse_events(html, today=date(2026, 10, 13))
    assert [event.title for event in result] == [
        "OKTAGON 95: KINCL VS. HUMBURGER",
        "OKTAGON 96: GOGOLADZE VS. KLINKHAMMER",
    ]
    assert result[0].venue == "Mattoni Arena, Karlovy Vary"


def test_past_events_and_invalid_dates_are_skipped():
    html = """
    <h2>OKTAGON 94: OLD EVENT</h2><p>26.09.2026 Arena, City</p>
    <h2>OKTAGON 95: BAD DATE</h2><p>99.10.2026 Arena, City</p>
    <h2>TIPSPORT CAGE GAME 2: TEST</h2><p>11.11.2026 BOBYHALL, Brno</p>
    """
    result = parse_events(html, today=date(2026, 10, 13))
    assert len(result) == 1
    assert result[0].day == date(2026, 11, 11)
