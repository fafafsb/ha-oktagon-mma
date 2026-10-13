# OKTAGON MMA for Home Assistant

Unofficial community integration for upcoming OKTAGON MMA events. Not affiliated with OKTAGON MMA.

## Current version: 0.2.0 (beta)

- Upcoming event calendar
- Next event title, date, venue, and days-until countdown sensors
- Event overview link in the next-event sensor attributes
- Countdown sensor refresh at local midnight
- German and English setup-flow translations
- Optional black-and-yellow dashboard card: [dashboard-premium.yaml](examples/dashboard-premium.yaml) (requires HACS button-card)

The public event source is scraped from the official event overview; page changes can break the parser. Event dates are currently **all-day**, not confirmed fight start times. Fight cards, alerts and live results are **not yet implemented**.

## Install with HACS

1. HACS > three-dot menu > Custom repositories.
2. Add `https://github.com/fafafsb/ha-oktagon-mma` as **Integration**.
3. Download OKTAGON MMA, restart Home Assistant.
4. Settings > Devices & services > Add integration > OKTAGON MMA.

## Updates and releases

The `manifest.json` version is `0.2.0`. Until a GitHub release/tag is published, HACS may show abbreviated commit hashes instead of semantic versions. Do not assume the manifest version creates a release automatically.

## Testing

GitHub Actions validates JSON, Python syntax, parser unit tests, and runs a live website smoke test. A green smoke test only confirms that at least five events are parsed; it does not validate every event or the HA runtime.

## Disclaimer

This is a fan-made, unofficial integration. Logos and trademarks belong to their respective owners.
