"""Conservative fight-card parser tests."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components" / "oktagon_mma"))
from fightcard import parse_fight_card, parse_visible_fight_card, find_event_page_url


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


def test_official_main_card_structure():
    html = """
    <h3>MAIN CARD</h3>
    <div>Middleweight</div><div>#2</div><div>#3</div>
    <div>Patrik Kincl</div><div>VS</div><div>Dominik Humburger</div>
    <div>Score (W-L-D)</div><div>30-12-0</div><div>12-3-0</div>
    <div>Show detail</div><div>Light heavyweight</div>
    <div>Daniel Škvor</div><div>VS</div><div>Tomasz Narkun</div>
    <div>Lightweight</div><div>Fighter</div><div>VS</div><div>TBA</div>
    """
    bouts = parse_visible_fight_card(html)
    assert len(bouts) == 2
    assert bouts[0].fighter_one == "Patrik Kincl"
    assert bouts[0].fighter_two == "Dominik Humburger"
    assert bouts[0].weight_class == "Middleweight"
    assert bouts[1].weight_class == "Light heavyweight"


def test_event_link_is_taken_from_official_overview():
    html = '<a href="/en/events/oktagon-95-karlovy-vary/">Fightcard</a>'
    assert find_event_page_url(html, "OKTAGON 95: KINCL VS. HUMBURGER") == (
        "https://oktagonmma.com/en/events/oktagon-95-karlovy-vary/"
    )
    assert find_event_page_url(html, "OKTAGON 96: OTHER") is None
