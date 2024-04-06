from pyserilog.core.string_writable import StringWriteable


class ThemedValueFormatterState:
    def __init__(self, output: StringWriteable, text_format: str = None, is_top_level: bool = False):
        self.output = output
        self.text_format = text_format
        self.is_top_level = is_top_level

    def nest(self):
        return ThemedValueFormatterState(output=self.output)
