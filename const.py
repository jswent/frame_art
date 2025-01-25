DOMAIN = "frame_art"

CONF_HOST = "host"
CONF_NAME = "name"
CONF_TIMEOUT = "timeout"

CONFIG_ENTRY_KEY = "hubs"

DEFAULT_TIMEOUT = 10.0
DEFAULT_PORT = 8002

ENABLE_SENSOR = False

SENSOR_TYPES = {
    "art_mode_status": {
        "name": "Art Mode Status",
        "unit_of_measurement": None,
        "icon": "mdi:television",
    },
    "brightness_level": {
        "name": "Brightness Level",
        "unit_of_measurement": "%",
        "icon": "mdi:brightness-6",
        "min": 0,
        "max": 100,
    },
    "connection_status": {
        "name": "Connection Status",
        "unit_of_measurement": None,
        "icon": "mdi:wifi",
    },
    "color_temperature": {
        "name": "Color Temperature",
        "unit_of_measurement": None,
        "icon": "mdi:thermometer",
        "min": -5,
        "max": 5,
    },
    "slideshow_status": {
        "name": "Slideshow Status",
        "unit_of_measurement": None,
        "icon": "mdi:image",
    },
    "current_image": {
        "name": "Current Image",
        "unit_of_measurement": None,
        "icon": "mdi:image",
    },
}

SERVICE_SET_BRIGHTNESS = "set_brightness"
SERVICE_SET_COLOR_TEMPERATURE = "set_color_temperature"

ATTR_BRIGHTNESS = "brightness"
ATTR_COLOR_TEMPERATURE = "color_temperature"

SUPPORTED_PLATFORMS = [
    "switch",
    "sensor",
    "media_player",
]
