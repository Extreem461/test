“”“Настройка конфигурации для интеграции полива газона.”””
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector
from homeassistant.helpers.entity_registry import async_get

from .const import (
DOMAIN,
CONF_ZONES,
CONF_MOISTURE_SENSORS,
CONF_WATERING_DURATION,
CONF_MOISTURE_THRESHOLD,
CONF_RAIN_THRESHOLD,
DEFAULT_WATERING_DURATION,
DEFAULT_MOISTURE_THRESHOLD,
DEFAULT_RAIN_THRESHOLD,
)

class LawnIrrigationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
“”“Обработка конфигурации интеграции.”””

```
VERSION = 1

async def async_step_user(self, user_input=None):
    """Обработка пользовательского ввода."""
    errors = {}
    
    if user_input is not None:
        # Проверка данных
        if not user_input.get(CONF_ZONES):
            errors[CONF_ZONES] = "no_zones_selected"
        else:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input
            )
    
    # Получение списка доступных переключателей и датчиков
    switches = await self._get_switches()
    sensors = await self._get_sensors()
    
    data_schema = vol.Schema({
        vol.Required(CONF_NAME, default="Полив газона"): str,
        vol.Required(CONF_ZONES, default=[]): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=switches,
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_MOISTURE_SENSORS, default=[]): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=sensors,
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_WATERING_DURATION, default=DEFAULT_WATERING_DURATION): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=120)
        ),
        vol.Optional(CONF_MOISTURE_THRESHOLD, default=DEFAULT_MOISTURE_THRESHOLD): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=100)
        ),
        vol.Optional(CONF_RAIN_THRESHOLD, default=DEFAULT_RAIN_THRESHOLD): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=50)
        ),
    })
    
    return self.async_show_form(
        step_id="user",
        data_schema=data_schema,
        errors=errors,
        description_placeholders={
            "switches_count": str(len(switches)),
            "sensors_count": str(len(sensors)),
        }
    )

async def _get_switches(self) -> list:
    """Получение списка доступных переключателей."""
    switches = []
    
    for entity_id, entity in self.hass.states.async_all().items():
        if entity_id.startswith("switch."):
            friendly_name = entity.attributes.get("friendly_name", entity_id)
            switches.append({"value": entity_id, "label": friendly_name})
    
    return switches

async def _get_sensors(self) -> list:
    """Получение списка доступных датчиков влажности."""
    sensors = []
    
    for entity_id, entity in self.hass.states.async_all().items():
        if entity_id.startswith("sensor."):
            # Поиск датчиков влажности по названию или атрибутам
            entity_name = entity_id.lower()
            friendly_name = entity.attributes.get("friendly_name", "").lower()
            device_class = entity.attributes.get("device_class", "").lower()
            
            if any(keyword in entity_name or keyword in friendly_name for keyword in 
                  ["moisture", "humidity", "влажность", "soil", "почва"]) or device_class == "humidity":
                display_name = entity.attributes.get("friendly_name", entity_id)
                sensors.append({"value": entity_id, "label": display_name})
    
    return sensors

@staticmethod
@config_entries.HANDLERS.register(DOMAIN)
def async_get_options_flow(config_entry):
    """Получение потока настроек опций."""
    return LawnIrrigationOptionsFlow(config_entry)
```

class LawnIrrigationOptionsFlow(config_entries.OptionsFlow):
“”“Поток настроек опций для интеграции.”””

```
def __init__(self, config_entry):
    """Инициализация потока опций."""
    self.config_entry = config_entry

async def async_step_init(self, user_input=None):
    """Обработка начального шага настроек."""
    if user_input is not None:
        return self.async_create_entry(title="", data=user_input)
    
    current_data = self.config_entry.data
    
    data_schema = vol.Schema({
        vol.Optional(
            CONF_WATERING_DURATION, 
            default=current_data.get(CONF_WATERING_DURATION, DEFAULT_WATERING_DURATION)
        ): vol.All(vol.Coerce(int), vol.Range(min=1, max=120)),
        vol.Optional(
            CONF_MOISTURE_THRESHOLD, 
            default=current_data.get(CONF_MOISTURE_THRESHOLD, DEFAULT_MOISTURE_THRESHOLD)
        ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(
            CONF_RAIN_THRESHOLD, 
            default=current_data.get(CONF_RAIN_THRESHOLD, DEFAULT_RAIN_THRESHOLD)
        ): vol.All(vol.Coerce(float), vol.Range(min=0, max=50)),
    })
    
    return self.async_show_form(
        step_id="init",
        data_schema=data_schema,
    )
```