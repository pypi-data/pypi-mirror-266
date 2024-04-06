from abc import abstractmethod

from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.log_event import LogEvent


class OutputTemplateTokenRenderer:

    @abstractmethod
    def render(self, log_event: LogEvent, output: StringWriteable):
        pass
