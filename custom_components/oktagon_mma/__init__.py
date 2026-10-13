"""OKTAGON MMA integration scaffold."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration; blocked until a verified data provider exists."""
    return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an entry."""
    return True
