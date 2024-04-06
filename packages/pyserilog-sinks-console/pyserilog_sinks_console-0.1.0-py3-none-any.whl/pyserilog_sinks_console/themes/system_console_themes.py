from pyserilog_sinks_console.themes.console_theme_style import ConsoleThemeStyle
from pyserilog_sinks_console.themes.system_console_theme import SystemConsoleTheme
from colorama import Fore, Style

LITERATE = SystemConsoleTheme({
    ConsoleThemeStyle.TEXT: Fore.WHITE,
    ConsoleThemeStyle.SECONDARY_TEXT: Fore.LIGHTBLACK_EX + Style.DIM,
    ConsoleThemeStyle.TERTIARY_TEXT: Fore.WHITE + Style.DIM,
    ConsoleThemeStyle.INVALID: Fore.YELLOW,
    ConsoleThemeStyle.NULL: Fore.BLUE,
    ConsoleThemeStyle.STRING: Fore.CYAN,
    ConsoleThemeStyle.NUMBER: Fore.MAGENTA,
    ConsoleThemeStyle.BOOLEAN: Fore.BLUE,
    ConsoleThemeStyle.SCALAR: Fore.GREEN,
    ConsoleThemeStyle.LEVEL_VERBOSE: Fore.LIGHTBLACK_EX + Style.DIM,
    ConsoleThemeStyle.LEVEL_DEBUG: Fore.LIGHTBLACK_EX + Style.DIM,
    ConsoleThemeStyle.LEVEL_INFORMATION: Fore.WHITE,
    ConsoleThemeStyle.LEVEL_WARNING: Fore.YELLOW,
    ConsoleThemeStyle.LEVEL_ERROR: Fore.RED,
    ConsoleThemeStyle.LEVEL_FATAL: Fore.RED,
})
