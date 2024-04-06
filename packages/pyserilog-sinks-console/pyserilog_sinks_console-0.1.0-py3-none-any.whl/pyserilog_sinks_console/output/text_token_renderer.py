from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.log_event import LogEvent

from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


class TextTokenRenderer(OutputTemplateTokenRenderer):
    def __init__(self, theme: ConsoleTheme, text: str):
        self._theme = theme
        self._text = text

    def render(self, log_event: LogEvent, output: StringWriteable):
        with self._theme.apply(output, ConsoleThemeStyle.TERTIARY_TEXT):
            output.write(self._text)
