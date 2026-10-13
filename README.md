# OKTAGON MMA for Home Assistant

Community integration (work in progress). Not affiliated with OKTAGON MMA.

## Planned v1
- Upcoming events calendar
- Next event, date, location, countdown and main-event sensors
- Fight card details when available
- UI setup and translations (German/English)

## Status
Initial project scaffold only. No live data provider is implemented yet. Do not install as a working integration.

## Architecture
`custom_components/oktagon_mma/` contains the Home Assistant custom integration. A data-source adapter will be added after validating a permitted and stable event feed. No personal credentials or external hosting should be required.

## Roadmap
1. Validate source and define event/fight schemas.
2. Implement async data client and coordinator with caching, retries and tests.
3. Implement config flow, calendar and sensors.
4. Add translations, documentation, CI and HACS validation.
5. Beta test and publish.
