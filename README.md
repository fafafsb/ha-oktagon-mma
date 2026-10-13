# OKTAGON MMA for Home Assistant

Unofficial community integration for upcoming OKTAGON MMA events. Not affiliated with OKTAGON MMA.

## Current development version: 0.3.1 (pre-release candidate)

- Upcoming event calendar
- Next event title, date, venue, and days-until countdown sensors
- Event overview link in the next-event sensor attributes
- Countdown sensor refresh at local midnight
- German and English setup-flow translations
- Optional black-and-yellow event dashboard: [dashboard-premium.yaml](examples/dashboard-premium.yaml) (requires HACS button-card)
- New dynamic fight card dashboard: [dashboard-fight-card.yaml](examples/dashboard-fight-card.yaml) (requires HACS button-card)
- Fight card sensor with fighter pairings, weight classes and main-event flag

The public event source is scraped from the official event overview; page changes can break the parser. Event dates are currently **all-day**, not confirmed fight start times. Fight card data is parsed from official event pages; alerts and live results are **not yet implemented**.

## Install with HACS

1. HACS > three-dot menu > Custom repositories.
2. Add `https://github.com/fafafsb/ha-oktagon-mma` as **Integration**.
3. Download OKTAGON MMA, restart Home Assistant.
4. Settings > Devices & services > Add integration > OKTAGON MMA.

## Updates and releases

The development `manifest.json` version is `0.3.1`. Until a GitHub release/tag is published, HACS may show abbreviated commit hashes instead of semantic versions. Do not assume the manifest version creates a release automatically.

## Testing

GitHub Actions validates JSON, Python syntax, parser unit tests, and runs a live website smoke test. A green smoke test only confirms that at least five events are parsed; it does not validate every event or the HA runtime.

## Disclaimer

This is a fan-made, unofficial integration. Logos and trademarks belong to their respective owners.

## Dynamic fight card dashboard (0.3.1 beta)

1. Install **button-card** from HACS > Frontend if not already installed.
2. Open [examples/dashboard-fight-card.yaml](examples/dashboard-fight-card.yaml) and copy its contents.
3. In your Home Assistant dashboard select **Edit > Add card > Manual** and paste the YAML.
4. If your entity ID differs, replace `sensor.next_oktagon_fight_card` in both `entity` and `triggers_update`.

The card automatically renders all bouts from the sensor's `fights` attribute. Tap the card to open the sensor details. This dashboard is a YAML example and is not automatically added to your dashboard when you install the integration.
