“”“Интеграция для автоматического полива газона.”””
import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(**name**)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
“”“Настройка интеграции из конфигурации.”””
coordinator = LawnIrrigationDataUpdateCoordinator(hass, entry)
await coordinator.async_config_entry_first_refresh()

```
hass.data.setdefault(DOMAIN, {})
hass.data[DOMAIN][entry.entry_id] = coordinator

await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
return True
```

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
“”“Удаление интеграции.”””
if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
hass.data[DOMAIN].pop(entry.entry_id)
return unload_ok

class LawnIrrigationDataUpdateCoordinator(DataUpdateCoordinator):
“”“Координатор обновления данных для полива газона.”””

```
def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
    """Инициализация координатора."""
    super().__init__(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=5),
    )
    self.entry = entry
    self.zones = entry.data.get("zones", [])
    self.moisture_sensors = entry.data.get("moisture_sensors", [])
    
async def _async_update_data(self):
    """Обновление данных."""
    data = {
        "zones": {},
        "moisture_levels": {},
        "weather_conditions": {},
    }
    
    # Получение данных о зонах полива
    for zone_id in self.zones:
        zone_entity = self.hass.states.get(zone_id)
        if zone_entity:
            data["zones"][zone_id] = {
                "state": zone_entity.state,
                "last_watered": zone_entity.attributes.get("last_watered"),
                "duration": zone_entity.attributes.get("duration", 0),
            }
    
    # Получение данных о влажности почвы
    for sensor_id in self.moisture_sensors:
        sensor_entity = self.hass.states.get(sensor_id)
        if sensor_entity:
            try:
                level = float(sensor_entity.state) if sensor_entity.state not in ['unavailable', 'unknown'] else 0
            except (ValueError, TypeError):
                level = 0
                
            data["moisture_levels"][sensor_id] = {
                "level": level,
                "unit": sensor_entity.attributes.get("unit_of_measurement", "%"),
            }
    
    # Получение погодных условий
    weather_entity = self.hass.states.get("weather.home")
    if weather_entity:
        data["weather_conditions"] = {
            "condition": weather_entity.state,
            "temperature": weather_entity.attributes.get("temperature"),
            "humidity": weather_entity.attributes.get("humidity"),
            "precipitation": weather_entity.attributes.get("precipitation", 0),
        }
    
    return data
```