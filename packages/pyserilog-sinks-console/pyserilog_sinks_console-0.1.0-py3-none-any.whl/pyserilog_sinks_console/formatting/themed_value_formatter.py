from abc import abstractmethod, ABC
from typing import Callable

from pyserilog import Guard
from pyserilog.core.string_writable import StringWriteable
from pyserilog.data.log_event_property_value_visitor import LogEventPropertyValueVisitor
from pyserilog.events.dictionary_value import DictionaryValue
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.events.sequence_value import SequenceValue
from pyserilog.events.structure_value import StructureValue

from pyserilog_sinks_console.formatting.themed_value_formatter_state import ThemedValueFormatterState
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle
from pyserilog_sinks_console.themes.style_reset import StyleReset


class ThemedValueFormatter(LogEventPropertyValueVisitor[ThemedValueFormatterState, int], ABC):
    def __init__(self, theme: ConsoleTheme):
        Guard.against_null(theme)
        self._theme = theme

    @abstractmethod
    def _visit_sequence_value(self, state: ThemedValueFormatterState, value: SequenceValue) -> int:
        pass

    @abstractmethod
    def _visit_structure_value(self, state: ThemedValueFormatterState, value: StructureValue) -> int:
        pass

    @abstractmethod
    def _visit_dictionary_value(self, state: ThemedValueFormatterState, value: DictionaryValue) -> int:
        pass

    @abstractmethod
    def _visit_scalar_value(self, state: ThemedValueFormatterState, value: ScalarValue) -> int:
        pass

    def apply_style(self, output: StringWriteable, style: ConsoleThemeStyle,
                    set_invisible_character_count_func: Callable[[int], None]) -> StyleReset:
        return self._theme.apply(output, style, set_invisible_character_count_func)

    def format(self, value: LogEventPropertyValue, output: StringWriteable, text_format: str | None,
               literal_top_level: bool = False) -> int:
        state = ThemedValueFormatterState(output, text_format, literal_top_level)
        return self.visit(state, value)
