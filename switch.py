“”“Переключатели для управления поливом.”””
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_ZONES, CONF_WATERING_DURATION, CONF_MOISTURE_THRESHOLD, CONF_RAIN_THRESHOLD

_LOGGER = logging.getLogger(**name**)

async def async_setup_entry(
hass: HomeAssistant,
config_entry: ConfigEntry,
async_add_entities: AddEntitiesCallback,
) -> None:
“”“Настройка переключателей.”””
coordinator = hass.data[DOMAIN][config_entry.entry_id]

```
entities = []

# Создание главного переключателя системы
entities.append(LawnIrrigationMasterSwitch(coordinator, config_entry))

# Создание переключателей для каждой зоны
for zone_id in coordinator.zones:
    entities.append(LawnIrrigationZoneSwitch(coordinator, config_entry, zone_id))

async_add_entities(entities)
```

class LawnIrrigationMasterSwitch(CoordinatorEntity, SwitchEntity):
“”“Главный переключатель системы полива.”””

```
def __init__(self, coordinator, config_entry):
    """Инициализация переключателя."""
    super().__init__(coordinator)
    self.config_entry = config_entry
    self._attr_name = "Система полива газона"
    self._attr_unique_id = f"{config_entry.entry_id}_master"
    self._attr_icon = "mdi:sprinkler"
    self._is_on = False
    self._watering_tasks = {}
    
@property
def is_on(self) -> bool:
    """Возвращает состояние переключателя."""
    return self._is_on

@property
def extra_state_attributes(self) -> dict[str, Any]:
    """Дополнительные атрибуты состояния."""
    zones_data = self.coordinator.data.get("zones", {})
    active_zones = [zone_id for zone_id, zone_data in zones_data.items() 
                   if zone_data.get("state") == "on"]
    
    return {
        "total_zones": len(self.coordinator.zones),
        "active_zones": len(active_zones),
        "active_zone_list": active_zones,
        "last_update": datetime.now().isoformat(),
        "watering_duration": self.config_entry.data.get(CONF_WATERING_DURATION, 30),
        "moisture_threshold": self.config_entry.data.get(CONF_MOISTURE_THRESHOLD, 30),
    }

async def async_turn_on(self, **kwargs: Any) -> None:
    """Включение системы полива."""
    self._is_on = True
    await self._start_automatic_irrigation()
    self.async_write_ha_state()

async def async_turn_off(self, **kwargs: Any) -> None:
    """Выключение системы полива."""
    self._is_on = False
    await self._stop_all_irrigation()
    self.async_write_ha_state()

async def _start_automatic_irrigation(self):
    """Запуск автоматического полива."""
    _LOGGER.info("Запуск автоматической системы полива")
    
    # Проверка погодных условий
    weather_data = self.coordinator.data.get("weather_conditions", {})
    rain_threshold = self.config_entry.data.get(CONF_RAIN_THRESHOLD, 5)
    
    if weather_data.get("precipitation", 0) > rain_threshold:
        _LOGGER.info("Полив отменен из-за дождя (осадки: %s мм)", weather_data.get("precipitation", 0))
        return
    
    # Проверка влажности почвы и запуск полива по зонам
    moisture_threshold = self.config_entry.data.get(CONF_MOISTURE_THRESHOLD, 30)
    
    for zone_id in self.coordinator.zones:
        # Поиск соответствующего датчика влажности
        moisture_level = await self._get_zone_moisture_level(zone_id)
        
        if moisture_level is not None and moisture_level < moisture_threshold:
            _LOGGER.info("Зона %s нуждается в поливе (влажность: %s%%)", zone_id, moisture_level)
            await self._water_zone(zone_id)
        else:
            _LOGGER.debug("Зона %s не нуждается в поливе (влажность: %s%%)", zone_id, moisture_level)

async def _get_zone_moisture_level(self, zone_id: str) -> float | None:
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

async def _water_zone(self, zone_id: str):
    """Полив отдельной зоны."""
    duration = self.config_entry.data.get(CONF_WATERING_DURATION, 30)
    
    # Включение переключателя зоны
    await self.hass.services.async_call(
        "switch", "turn_on", {"entity_id": zone_id}
    )
    
    _LOGGER.info("Запущен полив зоны %s на %d минут", zone_id, duration)
    
    # Запланированное выключение
    def turn_off_zone():
        """Выключение зоны по таймеру."""
        self.hass.async_create_task(
            self.hass.services.async_call(
                "switch", "turn_off", {"entity_id": zone_id}
            )
        )
        self._watering_tasks.pop(zone_id, None)
        _LOGGER.info("Полив зоны %s завершен", zone_id)
    
    # Отмена предыдущего таймера если он есть
    if zone_id in self._watering_tasks:
        self._watering_tasks[zone_id].cancel()
    
    # Запуск нового таймера
    self._watering_tasks[zone_id] = self.hass.loop.call_later(
        duration * 60, turn_off_zone
    )

async def _stop_all_irrigation(self):
    """Остановка всего полива."""
    _LOGGER.info("Остановка всего полива")
    
    # Отмена всех таймеров
    for task in self._watering_tasks.values():
        task.cancel()
    self._watering_tasks.clear()
    
    # Выключение всех зон
    for zone_id in self.coordinator.zones:
        await self.hass.services.async_call(
            "switch", "turn_off", {"entity_id": zone_id}
        )
```

class LawnIrrigationZoneSwitch(CoordinatorEntity, SwitchEntity):
“”“Переключатель для отдельной зоны полива.”””

```
def __init__(self, coordinator, config_entry, zone_id):
    """Инициализация переключателя зоны."""
    super().__init__(coordinator)
    self.config_entry = config_entry
    self.zone_id = zone_id
    self._attr_name = f"Полив {self._get_zone_name(zone_id)}"
    self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone_id.replace('.', '_')}"
    self._attr_icon = "mdi:sprinkler-variant"
    self._last_watered = None
    
def _get_zone_name(self, zone_id: str) -> str:
    """Получение читаемого имени зоны."""
    # Получение friendly_name из состояния сущности
    entity_state = self.hass.states.get(zone_id)
    if entity_state:
        friendly_name = entity_state.attributes.get("friendly_name")
        if friendly_name:
            return friendly_name
    
    # Если нет friendly_name, используем ID
    return zone_id.replace("switch.", "").replace("_", " ").title()

@property
def is_on(self) -> bool:
    """Возвращает состояние переключателя."""
    zone_data = self.coordinator.data.get("zones", {}).get(self.zone_id, {})
    return zone_data.get("state") == "on"

@property
def extra_state_attributes(self) -> dict[str, Any]:
    """Дополнительные атрибуты состояния."""
    zone_data = self.coordinator.data.get("zones", {}).get(self.zone_id, {})
    
    # Поиск соответствующего датчика влажности
    moisture_level = None
    moisture_unit = "%"
    moisture_data = self.coordinator.data.get("moisture_levels", {})
    
    for sensor_id, sensor_data in moisture_data.items():
        if self.zone_id in sensor_id or any(keyword in sensor_id.lower() for keyword in 
                                          self.zone_id.lower().split("_")):
            moisture_level = sensor_data.get("level", 0)
            moisture_unit = sensor_data.get("unit", "%")
            break
    
    return {
        "zone_id": self.zone_id,
        "zone_name": self._get_zone_name(self.zone_id),
        "last_watered": zone_data.get("last_watered"),
        "duration": zone_data.get("duration", 0),
        "moisture_level": moisture_level,
        "moisture_unit": moisture_unit,
        "watering_duration": self.config_entry.data.get(CONF_WATERING_DURATION, 30),
    }

async def async_turn_on(self, **kwargs: Any) -> None:
    """Включение полива зоны."""
    await self.hass.services.async_call(
        "switch", "turn_on", {"entity_id": self.zone_id}
    )
    self._last_watered = datetime.now()
    self.async_write_ha_state()
    _LOGGER.info("Ручное включение полива зоны %s", self.zone_id)

async def async_turn_off(self, **kwargs: Any) -> None:
    """Выключение полива зоны."""
    await self.hass.services.async_call(
        "switch", "turn_off", {"entity_id": self.zone_id}
    )
    self.async_write_ha_state()
    _LOGGER.info("Ручное выключение полива зоны %s", self.zone_id)
```