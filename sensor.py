“”“Датчики для мониторинга полива.”””
import logging
from datetime import datetime, timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import PERCENTAGE, UnitOfTime

from .const import DOMAIN, CONF_ZONES, CONF_MOISTURE_THRESHOLD

_LOGGER = logging.getLogger(**name**)

async def async_setup_entry(
hass: HomeAssistant,
config_entry: ConfigEntry,
async_add_entities: AddEntitiesCallback,
) -> None:
“”“Настройка датчиков.”””
coordinator = hass.data[DOMAIN][config_entry.entry_id]

```
entities = []

# Датчик общего статуса системы
entities.append(IrrigationSystemStatusSensor(coordinator, config_entry))

# Датчики влажности для каждой зоны
for zone_id in coordinator.zones:
    entities.append(ZoneMoistureSensor(coordinator, config_entry, zone_id))

# Датчик следующего полива
entities.append(NextWateringTimeSensor(coordinator, config_entry))

# Датчик общей влажности
entities.append(AverageMoistureSensor(coordinator, config_entry))

async_add_entities(entities)
```

class IrrigationSystemStatusSensor(CoordinatorEntity, SensorEntity):
“”“Датчик общего статуса системы полива.”””

```
def __init__(self, coordinator, config_entry):
    """Инициализация датчика."""
    super().__init__(coordinator)
    self.config_entry = config_entry
    self._attr_name = "Статус системы полива"
    self._attr_unique_id = f"{config_entry.entry_id}_system_status"
    self._attr_icon = "mdi:information"
    
@property
def native_value(self) -> str:
    """Возвращает текущий статус системы."""
    zones_data = self.coordinator.data.get("zones", {})
    active_zones = [zone_id for zone_id, zone_data in zones_data.items() 
                   if zone_data.get("state") == "on"]
    
    if active_zones:
        return f"Активно (зон: {len(active_zones)})"
    else:
        return "Готов к работе"

@property
def extra_state_attributes(self):
    """Дополнительные атрибуты."""
    zones_data = self.coordinator.data.get("zones", {})
    weather_data = self.coordinator.data.get("weather_conditions", {})
    moisture_data = self.coordinator.data.get("moisture_levels", {})
    
    active_zones = [zone_id for zone_id, zone_data in zones_data.items() 
                   if zone_data.get("state") == "on"]
    
    # Подсчет зон, нуждающихся в поливе
    moisture_threshold = self.config_entry.data.get(CONF_MOISTURE_THRESHOLD, 30)
    zones_need_watering = []
    
    for zone_id in self.coordinator.zones:
        moisture_level = self._get_zone_moisture_level(zone_id)
        if moisture_level is not None and moisture_level < moisture_threshold:
            zones_need_watering.append(zone_id)
    
    return {
        "total_zones": len(self.coordinator.zones),
        "active_zones": len(active_zones),
        "active_zone_list": active_zones,
        "zones_need_watering": len(zones_need_watering),
        "zones_need_watering_list": zones_need_watering,
        "weather_condition": weather_data.get("condition", "unknown"),
        "temperature": weather_data.get("temperature"),
        "humidity": weather_data.get("humidity"),
        "precipitation": weather_data.get("precipitation", 0),
        "last_update": datetime.now().isoformat(),
    }

def _get_zone_moisture_level(self, zone_id: str) -> float | None:
    """Получение уровня влажности для зоны."""
    moisture_data = self.coordinator.data.get("moisture_levels", {})
    
    # Поиск датчика влажности для конкретной зоны
    for sensor_id, sensor_data in moisture_data.items():
        if zone_id in sensor_id or any(keyword in sensor_id.lower() for keyword in 
                                     zone_id.lower().split("_")):
            return sensor_data.get("level", 0)
    
    # Если не найден специфический датчик, используем первый доступный
    if moisture_data:
        return next(iter(moisture_data.values())).get("level", 0)
    
    return None
```

class ZoneMoistureSensor(CoordinatorEntity, SensorEntity):
“”“Датчик влажности почвы для зоны.”””

```
def __init__(self, coordinator, config_entry, zone_id):
    """Инициализация датчика влажности."""
    super().__init__(coordinator)
    self.config_entry = config_entry
    self.zone_id = zone_id
    self._attr_name = f"Влажность {self._get_zone_name(zone
```