import logging
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, SensorStateClass
from homeassistant.const import (
    CONF_NAME, CONF_UNIQUE_ID, CONF_ENTITY_ID, ATTR_UNIT_OF_MEASUREMENT, ATTR_ICON
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_HYSTERESIS = 'hysteresis'
DEFAULT_NAME = "Hysteresis Sensor"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENTITY_ID): cv.entity_id,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_UNIQUE_ID): cv.string,
    vol.Required(CONF_HYSTERESIS): vol.Coerce(float),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Hysteresis sensor."""
    entity_id = config[CONF_ENTITY_ID]
    name = config[CONF_NAME]
    unique_id = config.get(CONF_UNIQUE_ID)
    hysteresis = config[CONF_HYSTERESIS]

    add_entities([HysteresisSensor(hass, entity_id, name, unique_id, hysteresis)])

class HysteresisSensor(SensorEntity):
    """Representation of a Hysteresis Sensor."""

    def __init__(self, hass, entity_id, name, unique_id, hysteresis):
        """Initialize the sensor."""
        self._hass = hass
        self._entity_id = entity_id
        self._name = name
        self._unique_id = unique_id
        self._hysteresis = hysteresis
        self._state = None
        self._unit_of_measurement = None
        self._icon = None

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def state_class(self):
        """Return the state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    def update(self):
        """Fetch new state data for the sensor."""
        input_state = self._hass.states.get(self._entity_id)
        if input_state is None:
            _LOGGER.warning("Entity %s not found", self._entity_id)
            return

        try:
            input_value = float(input_state.state)
        except ValueError:
            _LOGGER.error("Invalid state for %s: %s", self._entity_id, input_state.state)
            return

        # Update the unit of measurement and icon from the input sensor
        if self._unit_of_measurement is None:
            self._unit_of_measurement = input_state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        
        if self._icon is None:
            self._icon = input_state.attributes.get(ATTR_ICON)

        if self._state is None or abs(input_value - self._state) >= self._hysteresis:
            self._state = input_value