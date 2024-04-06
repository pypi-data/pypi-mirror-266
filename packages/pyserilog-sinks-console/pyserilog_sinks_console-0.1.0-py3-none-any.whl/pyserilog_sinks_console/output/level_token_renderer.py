from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.formatting.display.level_output_format import LevelOutputFormat
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.rendering.padding import Padding

from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


class LevelTokenRenderer(OutputTemplateTokenRenderer):
    levels = {
        LogEventLevel.VERBOSE: ConsoleThemeStyle.LEVEL_VERBOSE,
        LogEventLevel.DEBUG: ConsoleThemeStyle.LEVEL_DEBUG,
        LogEventLevel.INFORMATION: ConsoleThemeStyle.LEVEL_INFORMATION,
        LogEventLevel.WARNING: ConsoleThemeStyle.LEVEL_WARNING,
        LogEventLevel.ERROR: ConsoleThemeStyle.LEVEL_ERROR,
        LogEventLevel.FATAL: ConsoleThemeStyle.LEVEL_FATAL
    }

    def __init__(self, theme: ConsoleTheme, level_token: PropertyToken):
        self._theme = theme
        self._level_token = level_token

    def render(self, log_event: LogEvent, output: StringWriteable):
        moniker = LevelOutputFormat.get_level_moniker(log_event.level, self._level_token.format)
        if log_event.level not in self.levels:
            level_style = ConsoleThemeStyle.INVALID
        else:
            level_style = self.levels[log_event.level]

        with self._theme.apply(output, level_style):
            Padding.apply(output, moniker, self._level_token.alignment)
