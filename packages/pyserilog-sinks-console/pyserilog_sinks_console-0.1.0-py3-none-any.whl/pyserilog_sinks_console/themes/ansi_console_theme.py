from pyserilog.core.string_writable import StringWriteable

from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


class AnsiConsoleTheme(ConsoleTheme):
    ANSI_STYLE_RESET = '\x1b[0m'

    def __init__(self, styles: dict[ConsoleThemeStyle: str]):
        self._styles = styles

    @property
    def can_buffer(self) -> bool:
        return True

    @property
    def reset_char_count(self) -> int:
        return len(self.ANSI_STYLE_RESET)

    def reset(self, output: StringWriteable):
        output.write(self.ANSI_STYLE_RESET)

    def set(self, output: StringWriteable, style: ConsoleThemeStyle):
        if style not in self._styles:
            return 0

        ansi_style: str = self._styles[style]
        output.write(ansi_style)
        return len(ansi_style)
