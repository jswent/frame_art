import logging
from typing import List
from functools import partial
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.config_entries import ConfigEntry

from . import FrameArtHub
from .const import DOMAIN, CONF_HOST

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the switches for Frame Art integration from a config entry."""
    _LOGGER.info("Setting up Frame Art switches for entry: %s", entry.data[CONF_HOST])

    # Retrieve the hub for this config entry
    hub: FrameArtHub = hass.data[DOMAIN][entry.entry_id]

    # Create and add the switch entity
    switches = [ArtSwitch(hub)]
    async_add_entities(switches)


class ArtSwitch(SwitchEntity):
    """Representation of an art mode switch."""

    def __init__(self, hub: FrameArtHub) -> None:
        """Initialize the switch."""
        self._hub = hub
        self._attr_name = f"{hub.name} Art Mode"
        self._attr_unique_id = f"{hub.host}_art_mode".replace(".", "_")
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug("Turning on art mode for %s", self._hub.name)
        await self._hub.ex(partial(self._hub._tv.set_artmode, "on"))
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.debug("Turning off art mode for %s", self._hub.name)
        await self._hub.ex(partial(self._hub._tv.set_artmode, "off"))
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_update(self):
        """Update the switch state."""
        _LOGGER.debug("Updating art mode status for %s", self._hub.name)
        status = await self._hub.ex(self._hub._tv.get_artmode)
        self._attr_is_on = status == "on"