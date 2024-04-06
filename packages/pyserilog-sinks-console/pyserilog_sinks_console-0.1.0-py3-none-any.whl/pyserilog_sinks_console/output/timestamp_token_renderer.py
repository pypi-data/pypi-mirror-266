from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.formatting.json.json_value_formatter import JsonValueFormatter
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.rendering.padding import Padding

from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


class TimestampTokenRenderer(OutputTemplateTokenRenderer):
    def __init__(self, theme: ConsoleTheme, token: PropertyToken):
        self._theme = theme
        self._token = token

    def render(self, log_event: LogEvent, output: StringWriteable):

        with self._theme.apply(output, ConsoleThemeStyle.SECONDARY_TEXT):
            timestamp_str = JsonValueFormatter.datetime_format(log_event.timestamp)
            if self._token.alignment is None:
                output.write(timestamp_str)
            else:
                Padding.apply(output, timestamp_str, self._token.alignment)
