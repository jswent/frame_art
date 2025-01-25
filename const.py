DOMAIN = "frame_art"

CONF_HOST = "host"
CONF_NAME = "name"
CONF_TIMEOUT = "timeout"

CONFIG_ENTRY_KEY = "hubs"

DEFAULT_TIMEOUT = 10.0
DEFAULT_PORT = 8002

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
    },
    "connection_status": {
        "name": "Connection Status",
        "unit_of_measurement": None,
        "icon": "mdi:wifi",
    },
}

SUPPORTED_PLATFORMS = ["switch"]
