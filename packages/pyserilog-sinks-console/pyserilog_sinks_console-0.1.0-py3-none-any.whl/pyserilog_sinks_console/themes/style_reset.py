from pyserilog.core.string_writable import StringWriteable

from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.istyle_reset import IStyleReset


class StyleReset(IStyleReset):

    def __init__(self, theme: ConsoleTheme, output: StringWriteable):
        self._theme = theme
        self._output = output

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._theme.reset(self._output)
