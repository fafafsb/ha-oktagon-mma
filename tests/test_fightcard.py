"""Conservative fight-card parser tests."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components" / "oktagon_mma"))
from fightcard import parse_fight_card


def test_extracts_only_explicit_competitors():
    html = """<script type="application/ld+json">
    {"@type":"SportsEvent","competitor":[{"name":"Fighter A"},{"name":"Fighter B"}]}
    </script>"""
    assert [(b.fighter_one, b.fighter_two) for b in parse_fight_card(html)] == [
        ("Fighter A", "Fighter B")
    ]


def test_headline_does_not_invent_fight_card():
    assert parse_fight_card("<h1>Fighter A vs Fighter B</h1>") == []


def test_malformed_json_is_ignored():
    assert parse_fight_card('<script type="application/ld+json">{broken}</script>') == []
