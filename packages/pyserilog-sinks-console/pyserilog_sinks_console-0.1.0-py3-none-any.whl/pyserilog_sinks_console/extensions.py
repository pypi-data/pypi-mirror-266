import threading

from pyserilog import Guard, LoggerConfiguration
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.events.level_alias import LevelAlias
from pyserilog.events.log_event_level import LogEventLevel
import sys

from pyserilog_sinks_console.console_sink import ConsoleSink
from pyserilog_sinks_console.output.output_template_renderer import OutputTemplateRenderer
from pyserilog_sinks_console.themes.console_theme import ConsoleTheme
import pyserilog_sinks_console.themes.system_console_themes as system_themes


class Extensions:
    DEFAULT_CONSOLE_OUTPUT_TEMPLATE = "[{timestamp:%H:%m:%s} {level:u3}] {message:lj}{new_line}{exception}"
    DEFAULT_SYNC_ROOT = threading.Lock()

    @staticmethod
    def console(sink_configuration: LoggerSinkConfiguration,
                restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
                output_template=DEFAULT_CONSOLE_OUTPUT_TEMPLATE,
                level_switch: LoggingLevelSwitch = None,
                standard_error_from_level: LogEventLevel = None,
                theme: ConsoleTheme = None,
                apply_theme_to_redirected_output: bool = False,
                sync_root: object = None
                ) -> LoggerConfiguration:
        Guard.against_null(sink_configuration)
        Guard.against_null(output_template)

        redirected = not apply_theme_to_redirected_output and (sys.stdout.isatty() or sys.stderr.isatty())

        applied_theme = ConsoleTheme.none() if redirected else theme if theme is not None else system_themes.LITERATE

        formatter = OutputTemplateRenderer(applied_theme, output_template)
        if sync_root is None:
            sync_root = Extensions.DEFAULT_SYNC_ROOT
        sink = ConsoleSink(applied_theme, formatter, standard_error_from_level, sync_root)
        return sink_configuration.sink(sink, restricted_to_minimum_level, level_switch)
