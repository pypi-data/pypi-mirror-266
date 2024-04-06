from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.log_event import LogEvent
from pyserilog.parsing.alignment import Alignment
from pyserilog.rendering.padding import Padding

from pyserilog_sinks_console.output.output_template_token_renderer import OutputTemplateTokenRenderer
import pyserilog_sinks_console.rendering.alignment_extensions as ext


class NewLineTokenRenderer(OutputTemplateTokenRenderer):
    def __init__(self, alignment: Alignment):
        self._alignment = alignment

    def render(self, log_event: LogEvent, output: StringWriteable):
        new_line = '\n'
        if self._alignment is not None:
            Padding.apply(output, new_line, ext.widen(self._alignment, len(new_line)))
        else:
            output.write(new_line)
