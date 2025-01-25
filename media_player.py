import logging
from typing import Optional
from functools import partial
import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
    STATE_PLAYING,
)

from . import FrameArtHub
from .const import (
    DOMAIN,
    SERVICE_SET_BRIGHTNESS,
    ATTR_BRIGHTNESS,
    SERVICE_SET_COLOR_TEMPERATURE,
    ATTR_COLOR_TEMPERATURE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Frame Art media player from config entry."""
    hub: FrameArtHub = hass.data[DOMAIN].get(entry.entry_id)
    if not hub:
        return

    async_add_entities([FrameArtMediaPlayer(hub)])

    # Register services
    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_SET_BRIGHTNESS,
        {vol.Required(ATTR_BRIGHTNESS): cv.positive_int},
        "async_set_brightness",
    )
    platform.async_register_entity_service(
        SERVICE_SET_COLOR_TEMPERATURE,
        {vol.Required(ATTR_COLOR_TEMPERATURE): cv.positive_int},
        "async_set_color_temperature",
    )


class FrameArtMediaPlayer(MediaPlayerEntity):
    """Frame Art Media Player."""

    def __init__(self, hub: FrameArtHub) -> None:
        """Initialize the media player."""
        self._hub = hub
        self._attr_name = f"{hub.name} Frame"
        self._attr_unique_id = f"{hub.name}_frame".replace(".", "_")
        self._attr_supported_features = (
            MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
        )
        self._attr_device_class = "tv"
        self._attr_available = False
        self._state = None
        self._attributes = {}

    @property
    def state(self):
        """Return the state of the device."""
        if not self._attr_available:
            return None
        if self._state == "on":
            return (
                STATE_PLAYING
                if self._attributes.get("slideshow_status") == "on"
                else STATE_ON
            )
        return STATE_OFF

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return self._attributes

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self._hub.ex(partial(self._hub._tv.set_artmode, "on"))

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self._hub.ex(partial(self._hub._tv.set_artmode, "off"))

    async def async_update(self) -> None:
        """Fetch new state data for this device."""
        try:
            # Check if TV is available
            is_alive = await self._hub.ex(self._hub._tv.is_alive)
            self._attr_available = is_alive

            if not self._attr_available:
                return

            # Update art mode status
            self._state = await self._hub.ex(self._hub._tv.get_artmode)

            # Update attributes
            brightness_info = await self._hub.ex(self._hub._tv.get_brightness)
            color_temp_info = await self._hub.ex(self._hub._tv.get_color_temperature)
            slideshow_info = await self._hub.ex(self._hub._tv.get_slideshow_status)
            current_image = await self._hub.ex(self._hub._tv.get_current)

            self._attributes = {
                "art_mode_status": self._state,
                "brightness_level": int(brightness_info.get("value", 0)) * 10
                if brightness_info
                else None,
                "color_temperature": int(color_temp_info.get("value", 0))
                if color_temp_info
                else None,
                "slideshow_status": slideshow_info.get("value")
                if slideshow_info
                else None,
                "current_image": current_image.get("content_id")
                if current_image
                else None,
                "connection_status": "Connected" if is_alive else "Disconnected",
            }

        except Exception as e:
            _LOGGER.error("Error updating media player: %s", str(e))
            self._attr_available = False

    async def async_set_brightness(self, brightness: int) -> None:
        """Set the brightness of the TV."""
        await self._hub.ex(partial(self._hub._tv.set_brightness, brightness / 10))

    async def async_set_color_temperature(self, color_temperature: int) -> None:
        """Set the color temperature of the TV."""
        await self._hub.ex(
            partial(self._hub._tv.set_color_temperature, color_temperature)
        )
