

from pyserilog import Guard
from pyserilog.core.string_writable import StringWriteable, StringIOWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.message_template import MessageTemplate
from pyserilog.events.structure_value import StructureValue
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.rendering.padding import Padding

from pyserilog_sinks_console.formatting.themed_display_value_formatter import ThemedDisplayValueFormatter
from pyserilog_sinks_console.formatting.themed_json_value_formatter import ThemedJsonValueFormatter
from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme

import pyserilog_sinks_console.rendering.alignment_extensions as ext


class PropertiesTokenRenderer(OutputTemplateTokenRenderer):
    def __init__(self, theme: ConsoleTheme, token: PropertyToken, output_template: MessageTemplate):
        Guard.against_null(theme)
        Guard.against_null(token)
        Guard.against_null(output_template)

        self._theme = theme
        self._token = token
        self._output_template = output_template

        is_json = False

        if token.format is not None:
            for c in token.format:
                if c == "j":
                    is_json = True
        self._value_formatter = ThemedJsonValueFormatter(theme) if is_json else ThemedDisplayValueFormatter(theme)

    def render(self, log_event: LogEvent, output: StringWriteable):
        def is_contain(x: str):
            return not (self.__template_contain_property_name(log_event.message_template, x) or \
                        self.__template_contain_property_name(self._output_template, x))

        included = list(map(lambda x: LogEventProperty(x, log_event.properties[x]),
                            {k: v for k, v in log_event.properties.items() if is_contain(k)})
                        )
        value = StructureValue(included)
        if self._token.alignment is None or not self._theme.can_buffer:
            self._value_formatter.format(value, output, None)
            return
        buffer = StringIOWriteable()
        invisible = self._value_formatter.format(value, buffer, None)
        val = buffer.getvalue()
        buffer.close()
        Padding.apply(output, val, ext.widen(self._token.alignment, invisible))

    @staticmethod
    def __template_contain_property_name(template: MessageTemplate, property_name: str):
        for token in template.tokens:
            if isinstance(token, PropertyToken) and property_name == token.property_name:
                return True
        return False
