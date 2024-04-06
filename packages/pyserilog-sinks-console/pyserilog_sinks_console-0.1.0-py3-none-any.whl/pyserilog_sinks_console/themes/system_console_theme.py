from pyserilog.core.string_writable import StringWriteable

from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle

from colorama import init, deinit, Style


class SystemConsoleTheme(ConsoleTheme):
    def __init__(self, styles: dict[ConsoleThemeStyle, str]):
        self._styles = styles

    @property
    def can_buffer(self) -> bool:
        return False

    @property
    def reset_char_count(self) -> int:
        return len(Style.RESET_ALL)

    def reset(self, output: StringWriteable):
        output.write(Style.RESET_ALL)
        deinit()

    def set(self, output: StringWriteable, style: ConsoleThemeStyle) -> int:
        init()
        if style not in self._styles:
            return
        code = self._styles[style]
        output.write(code)
        return len(code)
