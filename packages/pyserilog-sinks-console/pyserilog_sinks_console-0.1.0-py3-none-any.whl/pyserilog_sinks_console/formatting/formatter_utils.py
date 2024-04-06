import math
from datetime import datetime
from decimal import Decimal

from pyserilog.core.string_writable import StringWriteable
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.formatting.json.json_value_formatter import JsonValueFormatter

from pyserilog_sinks_console.formatting.themed_value_formatter import ThemedValueFormatter
from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle


def format_number_value(value, output: StringWriteable):
    if math.isnan(value):
        JsonValueFormatter.write_quoted_json_string(output=output, value="NaN")
    elif math.isinf(value):
        if value > 0:
            JsonValueFormatter.write_quoted_json_string(output=output, value="Infinity")
        else:
            JsonValueFormatter.write_quoted_json_string(output=output, value="-Infinity")
    else:
        output.write(str(value))


def format_literal_value(formatter: ThemedValueFormatter, scalar: ScalarValue, output: StringWriteable,
                         text_format: str | None = None) -> int:
    value = scalar.value
    count = {'res': 0}

    def update_count_for_lit(x: int):
        count['res'] += x

    if value is None:
        with formatter.apply_style(output, ConsoleThemeStyle.NULL, update_count_for_lit):
            output.write("null")
        return count['res']
    if isinstance(value, str):
        with(formatter.apply_style(output, ConsoleThemeStyle.STRING, update_count_for_lit)):
            if text_format is None or text_format != "l":
                JsonValueFormatter.write_quoted_json_string(value, output)
            else:
                output.write(value)
        return count['res']

    if isinstance(value, bool):
        text = "true" if value else "false"
        with(formatter.apply_style(output, ConsoleThemeStyle.STRING, update_count_for_lit)):
            output.write(text)
        return count['res']

    if isinstance(value, int) or isinstance(value, float):
        with(formatter.apply_style(output, ConsoleThemeStyle.NUMBER, update_count_for_lit)):
            if text_format is None:
                format_number_value(value, output)
            else:
                scalar.render(output, text_format)
        return count['res']

    if isinstance(value, datetime):
        with(formatter.apply_style(output, ConsoleThemeStyle.SCALAR, update_count_for_lit)):
            datetime_str = JsonValueFormatter.datetime_format(value)
            output.write('"')
            output.write(datetime_str)
            output.write('"')
        return count['res']

    if isinstance(value, Decimal):
        with(formatter.apply_style(output, ConsoleThemeStyle.NUMBER, update_count_for_lit)):
            output.write(str(value))
        return count['res']

    raise count['res']
