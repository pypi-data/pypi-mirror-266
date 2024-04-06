from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.formatting.display.output_properties import OutputProperties
from pyserilog.formatting.itext_formatter import ITextFormatter
from pyserilog.guard import Guard
from pyserilog.parsing.message_template_parser import MessageTemplateParser
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.parsing.text_token import TextToken

from pyserilog_sinks_console.output.event_property_token_renderer import EventPropertyTokenRenderer
from pyserilog_sinks_console.output.exception_token_renderer import ExceptionTokenRenderer
from pyserilog_sinks_console.output.level_token_renderer import LevelTokenRenderer
from pyserilog_sinks_console.output.message_template_output_token_renderer import MessageTemplateOutputTokenRenderer
from pyserilog_sinks_console.output.new_line_token_renderer import NewLineTokenRenderer
from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
from pyserilog_sinks_console.output.properties_token_renderer import PropertiesTokenRenderer
from pyserilog_sinks_console.output.text_token_renderer import TextTokenRenderer
from pyserilog_sinks_console.output.timestamp_token_renderer import TimestampTokenRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme


class OutputTemplateRenderer(ITextFormatter):
    def __init__(self, theme: ConsoleTheme, output_template: str):
        Guard.against_null(theme)

        self.__renderers: list[OutputTemplateTokenRenderer] = []

        template = MessageTemplateParser().parse(output_template)
        for token in template.tokens:
            if isinstance(token, TextToken):
                self.__renderers.append(TextTokenRenderer(theme, token.text))
                continue
            assert isinstance(token, PropertyToken)

            if token.property_name == OutputProperties.LEVEL_PROPERTY_NAME:
                self.__renderers.append(LevelTokenRenderer(theme, token))
            elif token.property_name == OutputProperties.NEW_LINE_PROPERTY_NAME:
                self.__renderers.append(NewLineTokenRenderer(token.alignment))
            elif token.property_name == OutputProperties.EXCEPTION_PROPERTY_NAME:
                self.__renderers.append(ExceptionTokenRenderer(theme))
            elif token.property_name == OutputProperties.MESSAGE_PROPERTY_NAME:
                self.__renderers.append(MessageTemplateOutputTokenRenderer(theme, token))
            elif token.property_name == OutputProperties.TIMESTAMP_PROPERTY_NAME:
                self.__renderers.append(TimestampTokenRenderer(theme, token))
            elif token.property_name == OutputProperties.PROPERTIES_PROPERTY_NAME:
                self.__renderers.append(PropertiesTokenRenderer(theme, token, template))
            else:
                self.__renderers.append(EventPropertyTokenRenderer(theme, token))

    def format(self, log_event: LogEvent, output: StringWriteable):
        Guard.against_null(log_event)
        Guard.against_null(output)

        for renderer in self.__renderers:
            renderer.render(log_event, output)
