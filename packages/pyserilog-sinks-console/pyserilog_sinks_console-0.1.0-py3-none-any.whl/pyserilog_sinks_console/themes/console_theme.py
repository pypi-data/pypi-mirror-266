import threading
from abc import ABC, abstractmethod

from typing import Callable

from pyserilog.core.string_writable import StringWriteable

from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle
from pyserilog_sinks_console.themes.istyle_reset import IStyleReset


def create_none():
    from pyserilog_sinks_console.themes.empty_console import EmptyConsoleTheme
    return EmptyConsoleTheme()


class ConsoleTheme(ABC):
    _lock = threading.Lock()
    _none = None

    @staticmethod
    def none():
        if ConsoleTheme._none is not None:
            return ConsoleTheme._none
        with ConsoleTheme._lock:
            if ConsoleTheme._none is not None:
                return ConsoleTheme._none
            ConsoleTheme._none = create_none()
        return ConsoleTheme._none

    @property
    @abstractmethod
    def can_buffer(self) -> bool:
        pass

    @property
    @abstractmethod
    def reset_char_count(self) -> int:
        pass

    @abstractmethod
    def reset(self, output: StringWriteable):
        pass

    @abstractmethod
    def set(self, output: StringWriteable, style: ConsoleThemeStyle)-> int:
        pass

    def apply(self, output: StringWriteable, style: ConsoleThemeStyle,
              increase_invisible_character_count_func: Callable[[int], None] = None) -> IStyleReset:
        set_value = self.set(output, style)
        if increase_invisible_character_count_func is not None:
            increase_invisible_character_count_func(set_value)
            increase_invisible_character_count_func(self.reset_char_count)

        from pyserilog_sinks_console.themes.style_reset import StyleReset

        return StyleReset(self, output)
