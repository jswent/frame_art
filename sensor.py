import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from . import FrameArtHub, DOMAIN
from .const import SENSOR_TYPES, ENABLE_SENSOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up sensors for Frame Art integration from a config entry."""

    # Retrieve the hub for this config entry
    hub: FrameArtHub = hass.data[DOMAIN].get(entry.entry_id)
    if not hub:
        _LOGGER.error("Hub not found for entry_id: %s", entry.entry_id)
        return

    # Create and add sensor entities for this hub if enabled
    if ENABLE_SENSOR:
        _LOGGER.info("Setting up Frame Art sensors for host: %s", entry.data["host"])
        sensors = [FrameArtSensor(hub, sensor_type, config) for sensor_type, config in SENSOR_TYPES.items()]
        async_add_entities(sensors)


class FrameArtSensor(SensorEntity):
    """Representation of a Frame Art sensor."""

    def __init__(self, hub: FrameArtHub, sensor_type: str, config: dict) -> None:
        """Initialize the sensor."""
        self._hub = hub
        self._type = sensor_type
        self._attr_name = f"{hub.name} {config['name']}"
        self._attr_unique_id = f"{hub.host}_{sensor_type}".replace(".", "_")
        self._attr_unit_of_measurement = config.get("unit_of_measurement")
        self._attr_icon = config.get("icon")
        self._attr_native_value = None
        self._attr_native_min_value = config.get("min")
        self._attr_native_max_value = config.get("max")
        _LOGGER.debug("Setting up sensor %s for hub %s", self._type, self._hub.name)

    async def async_update(self) -> None:
        """Fetch the latest state of the sensor."""
        _LOGGER.debug("Updating sensor %s for hub %s", self._type, self._hub.name)

        # Check if TV is available
        try:
            is_alive = await self._hub.ex(self._hub._tv.is_alive)
            self._attr_available = is_alive
        except Exception as e:
            _LOGGER.debug("Error checking TV availability: %s", str(e))
            self._attr_available = False
            return

        if not self._attr_available:
            return

        try:
            if self._type == "art_mode_status":
                value = await self._hub.ex(self._hub._tv.get_artmode)
                if value is None:
                    self._attr_available = False
                    return
                self._attr_native_value = value

            elif self._type == "brightness_level":
                info = await self._hub.ex(self._hub._tv.get_brightness)
                if info is None:
                    self._attr_available = False
                    return
                try:
                    value = int(info.get("value", 0))
                    self._attr_native_value = value * 10
                except (ValueError, TypeError):
                    _LOGGER.warning("Could not parse brightness value from: %s", info)
                    self._attr_native_value = 0

            elif self._type == "connection_status":
                self._attr_native_value = "Connected" if is_alive else "Disconnected"

            elif self._type == "color_temperature":
                info = await self._hub.ex(self._hub._tv.get_color_temperature)
                if info is None:
                    self._attr_available = False
                    return
                try:
                    value = int(info.get("value", 0))
                    self._attr_native_value = value
                except (ValueError, TypeError):
                    _LOGGER.warning("Could not parse color temperature value from: %s", info)
                    self._attr_native_value = 0

            elif self._type == "slideshow_status":
                info = await self._hub.ex(self._hub._tv.get_slideshow_status)
                if info is None:
                    self._attr_available = False
                    return
                value = info.get("value")
                if value is None:
                    self._attr_available = False
                    return
                self._attr_native_value = value

            elif self._type == "current_image":
                info = await self._hub.ex(self._hub._tv.get_current)
                if info is None:
                    self._attr_available = False
                    return
                value = info.get("content_id")
                if value is None:
                    self._attr_available = False
                    return
                self._attr_native_value = value
                    
            else:
                _LOGGER.warning("Unknown sensor type: %s", self._type)
                self._attr_native_value = None

        except Exception as e:
            _LOGGER.error("Error updating %s sensor: %s", self._type, str(e))
            self._attr_available = False
