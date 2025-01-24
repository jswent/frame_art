"""Config flow for Samsung Frame Art integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_HOST, CONF_NAME, CONF_TIMEOUT, DEFAULT_TIMEOUT


class FrameArtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Frame Art."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate input
            host = user_input[CONF_HOST]
            try:
                # Example: Validate the host or IP address here
                if not self._is_valid_host(host):
                    errors["base"] = "invalid_host"
                else:
                    # Check if the host is already configured
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()

                    # Create the config entry
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME, host),
                        data={
                            CONF_HOST: host,
                            CONF_NAME: user_input.get(CONF_NAME, host),
                            CONF_TIMEOUT: user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
                        },
                    )
            except Exception:
                errors["base"] = "connection_failed"

        # Default form schema
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME): str,
                vol.Optional(CONF_TIMEOUT): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    def _is_valid_host(self, host: str) -> bool:
        """Validate the host (e.g., an IP address or hostname)."""
        # Placeholder validation logic, you can improve this
        import socket

        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow handler."""
        return FrameArtOptionsFlow(config_entry)


class FrameArtOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Samsung Frame Art."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Update the config entry options
            return self.async_create_entry(title="", data=user_input)

        # Default options schema
        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_TIMEOUT,
                    default=self.config_entry.options.get(
                        CONF_TIMEOUT, DEFAULT_TIMEOUT
                    ),
                ): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
