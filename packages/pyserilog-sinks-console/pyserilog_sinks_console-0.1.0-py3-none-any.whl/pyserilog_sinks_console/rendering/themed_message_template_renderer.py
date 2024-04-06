

from pyserilog import Guard
from pyserilog.core.string_writable import StringWriteable, StringIOWriteable
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.message_template import MessageTemplate
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.parsing.text_token import TextToken
from pyserilog.rendering.padding import Padding

from pyserilog_sinks_console.formatting.themed_value_formatter import ThemedValueFormatter
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle

import pyserilog_sinks_console.rendering.alignment_extensions as ali_ext


class ThemedMessageTemplateRenderer:

    def __init__(self, theme: ConsoleTheme, value_formatter: ThemedValueFormatter, is_literal: bool):
        Guard.against_null(theme)
        Guard.against_null(value_formatter)

        self._theme = theme
        self._value_formatter = value_formatter
        self._is_literal = is_literal

    def render(self, template: MessageTemplate, properties: dict[str, LogEventPropertyValue], output: StringWriteable) -> int:
        count = 0

        for token in template.tokens:
            if isinstance(token, TextToken):
                count += self._render_rext_token(token, output)
            else:
                assert isinstance(token, PropertyToken)
                count += self._render_property_token(token, properties, output)

        return count

    def _render_rext_token(self, token: TextToken, output: StringWriteable):
        count = {'res': 0}

        def update_count_in_text_token(x: int):
            count['res'] += x

        with self._theme.apply(output, ConsoleThemeStyle.TEXT, update_count_in_text_token):
            output.write(token.text)

        return count['res']

    def _render_property_token(self, token: PropertyToken, properties: dict[str, LogEventPropertyValue],
                               output: StringWriteable) -> int:
        if token.property_name not in properties:
            return self.__render_str(output, str(token), ConsoleThemeStyle.INVALID, self._theme)

        property_value = properties[token.property_name]
        if token.alignment is None:
            return self.__render_value(self._theme, self._value_formatter, property_value, output, token.format)

        buffer = StringIOWriteable()
        if not self._theme.can_buffer:
            raise NotImplementedError
        invisible_count = self.__render_value(self._theme, self._value_formatter, property_value, buffer, token.format)
        value = buffer.getvalue()
        buffer.close()
        if len(value) - invisible_count >= token.alignment.width:
            output.write(value)
        else:
            Padding.apply(output, value, ali_ext.widen(token.alignment, invisible_count))
        return invisible_count

    @staticmethod
    def __render_str(output: StringWriteable, value: str, style: ConsoleThemeStyle, theme: ConsoleTheme) -> int:
        count = {'res': 0}

        def update_count_res(x: int):
            count['res'] += x

        with theme.apply(output, style, update_count_res):
            output.write(value)
        return count['res']

    def __render_value(self, theme: ConsoleTheme, value_formatter: ThemedValueFormatter,
                       property_value: LogEventPropertyValue, output: StringWriteable, text_format: str | None) -> int:
        if self._is_literal and isinstance(property_value, ScalarValue) and isinstance(property_value.value, str):
            return self.__render_str(output, property_value.value, ConsoleThemeStyle.STRING, theme)
        return value_formatter.format(property_value, output, text_format, self._is_literal)
