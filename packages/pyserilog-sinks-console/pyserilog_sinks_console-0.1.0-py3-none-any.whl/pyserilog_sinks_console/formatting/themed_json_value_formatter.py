from pyserilog import Guard
from pyserilog.events.dictionary_value import DictionaryValue
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.events.sequence_value import SequenceValue
from pyserilog.events.structure_value import StructureValue
from pyserilog.formatting.json.json_value_formatter import JsonValueFormatter
from pyserilog_sinks_console.formatting.themed_value_formatter import ThemedValueFormatter
from pyserilog_sinks_console.formatting.themed_value_formatter_state import ThemedValueFormatterState
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle

import pyserilog_sinks_console.formatting.formatter_utils as utils


class ThemedJsonValueFormatter(ThemedValueFormatter):
    def __init__(self, theme: ConsoleTheme):
        super().__init__(theme)

    def _visit_sequence_value(self, state: ThemedValueFormatterState, value: SequenceValue) -> int:
        Guard.against_null(value)

        count = {'res': 0}
        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, lambda x: self.__update_count(x, count)):
            state.output.write("[")
        delim = ""
        for element in value.elements:
            if len(delim) > 0:
                with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT,
                                      lambda x: self.__update_count(x, count)):
                    state.output.write(delim)
            delim = ", "
            self.visit(state.nest(), element)

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, lambda x: self.__update_count(x, count)):
            state.output.write("]")
        return count['res']

    def _visit_structure_value(self, state: ThemedValueFormatterState, value: StructureValue) -> int:
        Guard.against_null(value)
        count = {'res': 0}

        def update_count_for_struct(x: int):
            count['res'] += x

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_struct):
            state.output.write("{")
        delim = self.__visit_structure_properties(count, state, update_count_for_struct, value)

        self.__visit_type_tag(delim, state, update_count_for_struct, value)

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_struct):
            state.output.write("}")
        return count['res']

    def __visit_structure_properties(self, count, state, update_count_for_struct, value):
        delim = ""
        for prop in value.properties:
            if len(delim) > 0:
                with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_struct):
                    state.output.write(delim)
            delim = ", "
            with self.apply_style(state.output, ConsoleThemeStyle.NAME, update_count_for_struct):
                JsonValueFormatter.write_quoted_json_string(prop.name, state.output)

            with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT,
                                  lambda x: self.__update_count(x, count)):
                state.output.write(": ")

            count['res'] += self.visit(state.nest(), prop.value)
        return delim

    def __visit_type_tag(self, delim, state, update_count_for_struct, value):
        if value.type_tag is not None:
            with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_struct):
                state.output.write(delim)

            with self.apply_style(state.output, ConsoleThemeStyle.NAME, update_count_for_struct):
                JsonValueFormatter.write_quoted_json_string("$type", state.output)

            with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_struct):
                state.output.write(": ")

            with self.apply_style(state.output, ConsoleThemeStyle.STRING, update_count_for_struct):
                JsonValueFormatter.write_quoted_json_string(value.type_tag, state.output)

    def _visit_dictionary_value(self, state: ThemedValueFormatterState, value: DictionaryValue) -> int:
        Guard.against_null(value)
        count = {'res': 0}

        def update_count_for_dict(x: int):
            count['res'] += x

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_dict):
            state.output.write("{")

        delim = ""
        for element_key, element_value in value.elements:

            if len(delim) > 0:
                with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_dict):
                    state.output.write(delim)
            delim = ", "

            style = ConsoleThemeStyle.NULL
            if element_key.value is not None:
                if isinstance(element_key.value, str):
                    style = ConsoleThemeStyle.STRING
                else:
                    style = ConsoleThemeStyle.SCALAR

            with self.apply_style(state.output, style, update_count_for_dict):
                value = "null" if element_key.value is None else str(element_key.value)
                JsonValueFormatter.write_quoted_json_string(value, state.output)

            with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_dict):
                state.output.write(": ")

            count['res'] += self.visit(state.nest(), element_value)

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_dict):
            state.output.write("}")
        return count['res']

    def _visit_scalar_value(self, state: ThemedValueFormatterState, value: ScalarValue) -> int:
        Guard.against_null(value)

        if state.is_top_level:
            raise NotImplementedError
        return utils.format_literal_value(self, value, state.output)

    @staticmethod
    def __update_count(x: int, count: dict):
        count['res'] += x
