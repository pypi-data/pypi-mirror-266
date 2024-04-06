from pyserilog.core.string_writable import StringIOWriteable, StringWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.rendering.casing import Casing
from pyserilog.rendering.padding import Padding

from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


class EventPropertyTokenRenderer(OutputTemplateTokenRenderer):
    def __init__(self, theme: ConsoleTheme, token: PropertyToken):
        self._theme = theme
        self._token = token

    def render(self, log_event: LogEvent, output: StringWriteable):
        if self._token.property_name not in log_event.properties:
            Padding.apply(output, "", self._token.alignment)
            return

        property_value = log_event.properties[self._token.property_name]
        with self._theme.apply(output, ConsoleThemeStyle.SECONDARY_TEXT):
            has_alignment = self._token.alignment is not None
            writer = StringIOWriteable() if has_alignment else output

            if isinstance(property_value, ScalarValue) and isinstance(property_value.value, str):
                cased = Casing.format(property_value.value, self._token.format)
                writer.write(cased)
            else:
                property_value.render(writer, self._token.format)

            if has_alignment:
                val = writer.getvalue()
                writer.close()
                Padding.apply(output, val, self._token.alignment)
