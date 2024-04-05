from datetime import datetime

from pyserilog.core.string_writable import StringWriteable

from pyserilog.guard import Guard
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.event_property import EventProperty
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.message_template import  MessageTemplate


class LogEvent:

    def __init__(self, timestamp: datetime, level: LogEventLevel, exception: Exception | None,
                 message_template: MessageTemplate,
                 properties: dict[str, LogEventPropertyValue] | list[LogEventProperty]):
        self._timestamp = timestamp
        self._level = level
        self._exception = exception
        self._message_template = message_template
        self._properties: dict[str, LogEventPropertyValue] = {}
        if isinstance(properties, dict):
            self._properties = properties
        elif isinstance(properties, list):
            for prop in properties:
                self.add_or_update_property(prop)

    @property
    def timestamp(self) -> datetime:
        """
        The time at which the event occurred.
        """
        return self._timestamp

    @property
    def level(self) -> LogEventLevel:
        """
        The level of the event.
        """
        return self._level

    @property
    def message_template(self) -> MessageTemplate:
        """
        The message template describing the event.
        """
        return self._message_template

    @property
    def properties(self) -> dict[str, LogEventPropertyValue]:
        return self._properties

    @property
    def exception(self) -> Exception | None:
        """
        An exception associated with the event, or null
        """
        return self._exception

    def render_message(self, output: StringWriteable | None = None):
        """
        Render the message template to the specified output, given the properties associated with the event.
        """
        if output is None:
            return self._message_template.render(properties=self._properties)
        else:
            return self._message_template.render(properties=self._properties, output=output)

    def add_or_update_property(self, prop: LogEventProperty | EventProperty):
        """
        Add a property to the event if not already present, otherwise, update its value.
        :param prop: The property to add or update.
        """
        Guard.against_null(prop)

        self._properties[prop.name] = prop.value

    def add_property_if_absent(self, prop: LogEventProperty | EventProperty):
        Guard.against_null(prop)

        if prop.name not in self._properties:
            self._properties[prop.name] = prop.value

    def remove_property_if_present(self, property_name: str):
        """
        Remove a property from the event, if present. Otherwise no action is performed.
        """
        self._properties.pop(property_name)

    def copy(self):
        properties = {}
        for property_name in self._properties:
            properties[property_name] = self._properties[property_name]

        return LogEvent(timestamp=self.timestamp, level=self.level, exception=self.exception,
                        message_template=self.message_template, properties=properties)
