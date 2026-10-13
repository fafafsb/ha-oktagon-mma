"""OKTAGON MMA integration."""
from pathlib import Path
import logging

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, CoreState, EVENT_HOMEASSISTANT_STARTED
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import OktagonCoordinator

PLATFORMS = ["calendar", "sensor"]
_LOGGER = logging.getLogger(__name__)
CARD_URLS = ("/oktagon_mma/oktagon-fight-card.js", "/oktagon_mma/oktagon-event-card.js")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from the Home Assistant UI."""
    coordinator = OktagonCoordinator(hass)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady("OKTAGON event source unavailable") from err
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await _async_register_card(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload platforms and release coordinator."""
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
        return True
    return False


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve both cards and register Lovelace resources after startup."""
    data = hass.data[DOMAIN]
    if data.get("_card_registered"):
        return
    static_files = [
        StaticPathConfig(url, str(Path(__file__).parent / "www" / url.rsplit("/", 1)[-1]), cache_headers=False)
        for url in CARD_URLS
    ]
    static_files.append(StaticPathConfig("/oktagon_mma/icon.png", str(Path(__file__).parent / "brand" / "icon.png"), cache_headers=False))
    await hass.http.async_register_static_paths(static_files)
    data["_card_registered"] = True

    async def register_resources(_event=None):
        try:
            from homeassistant.components.lovelace.const import LOVELACE_DATA, MODE_STORAGE
            lovelace = hass.data.get(LOVELACE_DATA)
            if lovelace is None or getattr(lovelace, "resource_mode", None) != MODE_STORAGE:
                _LOGGER.warning("OKTAGON resource auto-registration requires Lovelace storage resource mode")
                return
            resources = getattr(lovelace, "resources", None)
            if resources is None or not hasattr(resources, "async_create_item"):
                _LOGGER.warning("OKTAGON Lovelace resources unavailable; add card URLs manually")
                return
            if not resources.loaded:
                await resources.async_load()
            existing = getattr(resources, "async_items", lambda: [])()
            for url in CARD_URLS:
                if not any(item.get("url", "").split("?")[0] == url for item in existing):
                    await resources.async_create_item({"res_type": "module", "url": url})
                    _LOGGER.info("Registered OKTAGON Lovelace card: %s", url)
        except Exception:
            _LOGGER.exception("Could not automatically register OKTAGON dashboard resources")

    if hass.state == CoreState.running:
        await register_resources()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, register_resources)
