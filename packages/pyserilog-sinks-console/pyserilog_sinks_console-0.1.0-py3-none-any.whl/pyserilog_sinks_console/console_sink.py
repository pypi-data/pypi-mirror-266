import sys

from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.core.string_writable import StringWriteable, StringIOWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.formatting import ITextFormatter

from pyserilog_sinks_console.themes.console_theme import ConsoleTheme


class StdOutStringIOWritable(StringWriteable):

    def write(self, value: str):
        sys.stdout.write(value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.flush()


class StdErrorStringIOWritable(StringWriteable):

    def write(self, value: str):
        sys.stderr.write(value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.flush()


std_out = StdOutStringIOWritable()
std_error = StdErrorStringIOWritable()


class ConsoleSink(ILogEventSink):
    def __init__(self, theme: ConsoleTheme, formatter: ITextFormatter, standard_error_from_level: LogEventLevel,
                 sync_root):
        self._theme = theme
        self._formatter = formatter
        self._sync_root = sync_root
        self._standard_error_from_level = standard_error_from_level

    def emit(self, log_event: LogEvent):
        with self.select_output_stream(log_event.level) as output:

            if self._theme.can_buffer:
                buffer = StringIOWriteable()
                self._formatter.format(log_event, buffer)
                formatted_log_event_text = buffer.getvalue()
                with self._sync_root:
                    output.write(formatted_log_event_text)
            else:
                with self._sync_root:
                    self._formatter.format(log_event, output)

    def select_output_stream(self, log_event_level: LogEventLevel) -> StringWriteable:
        if self._standard_error_from_level is None:
            return std_out
        return std_out if log_event_level < self._standard_error_from_level else std_error
