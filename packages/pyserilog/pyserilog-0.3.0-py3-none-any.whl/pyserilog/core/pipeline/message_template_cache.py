import threading

from pyserilog.guard import Guard
from pyserilog.core.imessage_template_parser import IMessageTemplateParser
from pyserilog.events.message_template import MessageTemplate


class MessageTemplateCache(IMessageTemplateParser):
    max_cache_items = 1000,
    max_cached_template_length = 1024
    _template_lock = threading.Lock()
    _templates = {}

    def __init__(self, inner_parser: IMessageTemplateParser):
        self._inner_parser = inner_parser

    def parse(self, message_template: str) -> MessageTemplate:
        Guard.against_null(message_template)

        if len(message_template) > self.max_cached_template_length:
            return self._inner_parser.parse(message_template)

        if message_template in self._templates:
            return self._templates[message_template]

        result = self._inner_parser.parse(message_template)
        with self._template_lock:
            """
            Exceeding MaxCacheItems is *not* the sunny day scenario; all we're doing here is preventing out-of-memory
            conditions when the library is used incorrectly. Correct use (templates, rather than
            direct message strings) should barely, if ever, overflow this cache.
            
            Changing workloads through the lifecycle of an app instance mean we can gain some ground by
            potentially dropping templates generated only in startup, or only during specific infrequent activities.
            """

            if len(self._templates) == self.max_cache_items:
                self._templates.clear()
            self._templates[message_template] = result

        return result
