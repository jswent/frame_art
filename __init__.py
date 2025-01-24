"""Samsung The Frame Art Switch."""

import logging
from typing import List, Dict, Any
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from .samsungtvws.async_art import SamsungTVAsyncArt
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_NAME,
    CONF_TIMEOUT,
    DEFAULT_TIMEOUT,
    DEFAULT_PORT,
    SUPPORTED_PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


class FrameArtHub:
    """A shared hub to manage Samsung Frame TV connections."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]) -> None:
        """Initialize the hub."""
        self.hass = hass
        self.host = config[CONF_HOST]
        self.name = config.get(CONF_NAME, self.host)
        self._tv = None
        self._token_file = f"{DOMAIN}_{self.host.replace('.', '_')}_token.txt"
        self._timeout = config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    async def async_initialize(self) -> None:
        """Initialize the TV connection."""
        _LOGGER.debug("Initializing TV connection for %s", self.host)
        try:
            self._tv = SamsungTVAsyncArt(
                self.host,
                timeout=self._timeout,
                port=DEFAULT_PORT,
                token_file=self._token_file,
            )
            await self._tv.initialize()
            _LOGGER.info("TV initialized at %s", self.host)
            await self._tv.start_listening()
            _LOGGER.info("Started listening to TV at %s", self.host)
        except Exception as e:
            _LOGGER.error("Failed to initialize TV connection for %s: %s", self.host, e)
            self._tv = None

    async def ex(self, callback) -> Any:
        """
        Execute a callback after ensuring the TV is initialized.

        Args:
            callback (Callable): A callable to execute, can be sync or async.

        Returns:
            Any: The result of the callback, or None if initialization failed.
        """
        if not self._tv:
            _LOGGER.warning(
                "TV at %s is not initialized. Attempting to reinitialize...", self.host
            )
            await self.async_initialize()
            if not self._tv:
                _LOGGER.error(
                    "Failed to initialize TV at %s. Callback cannot be executed.",
                    self.host,
                )
                return None

        try:
            if asyncio.iscoroutinefunction(callback):
                return await callback()
            else:
                return callback()
        except Exception as e:
            _LOGGER.error("Error executing callback for TV at %s: %s", self.host, e)
            return None


# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Set up the Frame Art integration."""
#     if DOMAIN not in config:
#         return True

#     hass.data.setdefault(DOMAIN, {})
#     hass.data[DOMAIN][CONFIG_ENTRY_KEY] = []

#     for entry in config[DOMAIN]:
#         hub = FrameArtHub(hass, entry)
#         await hub.async_initialize()
#         hass.data[DOMAIN][CONFIG_ENTRY_KEY].append(hub)

#     # Load the switch platform
#     hass.async_create_task(
#         hass.helpers.discovery.async_load_platform("switch", DOMAIN, {}, config)
#     )

#     return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Frame Art integration from a config entry."""
    _LOGGER.info(
        "Setting up Samsung Frame Art integration for host: %s", entry.data[CONF_HOST]
    )

    # Initialize the DOMAIN in hass.data
    hass.data.setdefault(DOMAIN, {})

    # Initialize a hub for this entry
    hub = FrameArtHub(hass, entry.data)
    await hub.async_initialize()

    # Store the hub in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub

    # Forward the entry setup to supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info(
        "Unloading Samsung Frame Art integration for host: %s", entry.data[CONF_HOST]
    )

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, SUPPORTED_PLATFORMS
    )

    # Remove the hub from hass.data
    if unload_ok:
        hub = hass.data[DOMAIN].pop(entry.entry_id, None)
        if hub:
            _LOGGER.info("Shutting down connection to TV at %s", hub.host)

    # Clean up if no hubs remain
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)

    return unload_ok
