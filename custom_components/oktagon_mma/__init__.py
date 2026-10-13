"""OKTAGON MMA integration."""
from pathlib import Path
import logging

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import OktagonCoordinator

PLATFORMS = ["calendar", "sensor"]
_LOGGER = logging.getLogger(__name__)
CARD_URL = "/oktagon_mma/oktagon-fight-card.js"


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
    """Expose bundled frontend card and register it in storage-mode Lovelace."""
    if hass.data[DOMAIN].get("_card_registered"):
        return
    card_file = Path(__file__).parent / "www" / "oktagon-fight-card.js"
    await hass.http.async_register_static_paths([
        StaticPathConfig(CARD_URL, str(card_file), cache_headers=False)
    ])
    hass.data[DOMAIN]["_card_registered"] = True
    try:
        from homeassistant.components.lovelace.const import DOMAIN as LOVELACE_DOMAIN

        lovelace = hass.data.get(LOVELACE_DOMAIN)
        resources = getattr(lovelace, "resources", None)
        if resources is None or not hasattr(resources, "async_create_item"):
            _LOGGER.info("OKTAGON card available at %s; add as a Lovelace resource if using YAML mode", CARD_URL)
            return
        if hasattr(resources, "async_load"):
            await resources.async_load()
        existing = getattr(resources, "async_items", lambda: [])()
        if not any(item.get("url", "").split("?")[0] == CARD_URL for item in existing):
            await resources.async_create_item({"res_type": "module", "url": CARD_URL})
    except Exception:
        _LOGGER.exception("Could not automatically register OKTAGON dashboard resource")
