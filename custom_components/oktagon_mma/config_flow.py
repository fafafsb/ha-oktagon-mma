"""UI configuration placeholder until the data provider is implemented."""

from homeassistant import config_entries
from .const import DOMAIN


class OktagonMMAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure OKTAGON MMA."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_abort(reason="not_implemented")
