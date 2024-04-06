from pyserilog.core.string_writable import StringWriteable, StringIOWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.rendering.padding import Padding

from pyserilog_sinks_console.formatting.themed_display_value_formatter import ThemedDisplayValueFormatter
from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.rendering.themed_message_template_renderer import ThemedMessageTemplateRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme

import pyserilog_sinks_console.rendering.alignment_extensions as ali_ext


class MessageTemplateOutputTokenRenderer(OutputTemplateTokenRenderer):

    def __init__(self, theme: ConsoleTheme, token: PropertyToken):
        self._theme = theme
        self._token = token

        is_literal = False
        is_json = False

        if token.format is not None:
            for c in token.format:
                if c == "l":
                    is_literal = True
                elif c == "j":
                    is_json = True
        value_formatter = ThemedDisplayValueFormatter(theme) if is_json else ThemedDisplayValueFormatter(theme)

        self._renderer = ThemedMessageTemplateRenderer(theme, value_formatter, is_literal)

    def render(self, log_event: LogEvent, output: StringWriteable):

        if self._token.alignment is None or not self._theme.can_buffer:
            self._renderer.render(log_event.message_template, log_event.properties, output)
            return

        buffer = StringIOWriteable()
        invisible = self._renderer.render(log_event.message_template, log_event.properties, buffer)
        value = buffer.getvalue()
        buffer.close()
        Padding.apply(output, value, ali_ext.widen(self._token.alignment, invisible))
