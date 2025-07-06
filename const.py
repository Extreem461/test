“”“Константы для интеграции полива газона.”””
from homeassistant.const import Platform

DOMAIN = “lawn_irrigation”
PLATFORMS = [Platform.SWITCH, Platform.SENSOR, Platform.BINARY_SENSOR]

# Настройки по умолчанию

DEFAULT_WATERING_DURATION = 30  # минут
DEFAULT_MOISTURE_THRESHOLD = 30  # %
DEFAULT_RAIN_THRESHOLD = 5  # мм

# Типы зон

ZONE_TYPES = {
“lawn”: “Газон”,
“garden”: “Сад”,
“flower_bed”: “Клумба”,
“vegetable_garden”: “Огород”,
}

# Конфигурационные ключи

CONF_ZONES = “zones”
CONF_MOISTURE_SENSORS = “moisture_sensors”
CONF_WATERING_DURATION = “watering_duration”
CONF_MOISTURE_THRESHOLD = “moisture_threshold”
CONF_RAIN_THRESHOLD = “rain_threshold”