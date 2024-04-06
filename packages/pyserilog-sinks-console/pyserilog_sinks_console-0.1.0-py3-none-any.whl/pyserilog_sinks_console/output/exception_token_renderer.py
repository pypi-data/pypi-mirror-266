from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.log_event import LogEvent

from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


class ExceptionTokenRenderer(OutputTemplateTokenRenderer):
    def __init__(self, theme: ConsoleTheme):
        self._theme = theme

    def render(self, log_event: LogEvent, output: StringWriteable):
        if log_event.exception is None:
            return

        with self._theme.apply(output, ConsoleThemeStyle.TEXT):
            output.write(str(log_event.exception))
        output.write("\n")
