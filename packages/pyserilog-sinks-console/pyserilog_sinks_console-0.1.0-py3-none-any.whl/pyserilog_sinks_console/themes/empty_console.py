from pyserilog.core.string_writable import StringWriteable

from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


class EmptyConsoleTheme(ConsoleTheme):
    @property
    def reset_char_count(self) -> int:
        return 0

    def set(self, output: StringWriteable, style: ConsoleThemeStyle):
        return 0

    def reset(self, output: StringWriteable):
        pass

    @property
    def can_buffer(self) -> bool:
        return True
