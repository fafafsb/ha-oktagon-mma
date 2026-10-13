"""User interface setup for OKTAGON MMA."""
from homeassistant import config_entries

from .const import DOMAIN


class OktagonMMAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Single-instance integration, no credentials required."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="OKTAGON MMA", data={})
        return self.async_show_form(step_id="user")
