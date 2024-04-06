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


class ThemedDisplayValueFormatter(ThemedValueFormatter):
    def __init__(self, theme: ConsoleTheme):
        super().__init__(theme)

    def _visit_sequence_value(self, state: ThemedValueFormatterState, value: SequenceValue) -> int:
        Guard.against_null(value)

        count = {'res': 0}

        def update_count_for_seq(x: int):
            count['res'] += x

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_seq):
            state.output.write("[")
        delim = ""
        for element in value.elements:
            if len(delim) > 0:
                with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_seq):
                    state.output.write(delim)
            delim = ", "
            self.visit(state.nest(), element)

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_seq):
            state.output.write("]")
        return count['res']

    def _visit_structure_value(self, state: ThemedValueFormatterState, value: StructureValue) -> int:
        Guard.against_null(value)
        count = {'res': 0}

        def update_count(x: int):
            count['res'] += x

        if value.type_tag is not None:
            with self.apply_style(state.output, ConsoleThemeStyle.NAME, update_count):
                state.output.write(value.type_tag)
            state.output.write(" ")
        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count):
            state.output.write("{")

        delim = ""
        for prop in value.properties:
            if len(delim) > 0:
                with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count):
                    state.output.write(delim)

            delim = ", "
            with self.apply_style(state.output, ConsoleThemeStyle.NAME, update_count):
                state.output.write(prop.name)

            with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count):
                state.output.write("=")
            count['res'] += self.visit(state.nest(), prop.value)

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count):
            state.output.write("}")
        return count['res']

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

            with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_dict):
                state.output.write("[")

            with self.apply_style(state.output, ConsoleThemeStyle.STRING, update_count_for_dict):
                count['res'] += self.visit(state.nest(), element_key)

            with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_dict):
                state.output.write("]=")

            count['res'] += self.visit(state.nest(), element_value)

        with self.apply_style(state.output, ConsoleThemeStyle.TERTIARY_TEXT, update_count_for_dict):
            state.output.write("}")
        return count['res']

    def _visit_scalar_value(self, state: ThemedValueFormatterState, value: ScalarValue) -> int:
        Guard.against_null(value)

        return utils.format_literal_value(self, value, state.output, state.text_format)
