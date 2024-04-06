
class ConsoleThemeStyle:
    TEXT = 1
    """
    Prominent text, generally content within an event's message.
    """
    SECONDARY_TEXT = 2
    """
    Boilerplate text, for example items specified in an output template.
    """
    TERTIARY_TEXT = 3
    """
    De-emphasized text, for example literal text in output templates and punctuation used when writing structured data.
    """
    INVALID = 4
    """
    Output demonstrating some kind of configuration issue, e.g. an invalid message template token.
    """
    NULL = 5
    """
    The built-in "none"
    """
    NAME = 6
    """
    Property and type names.
    """
    STRING = 7
    """
    Strings.
    """
    NUMBER = 8
    """
    Numbers.
    """
    BOOLEAN = 9
    """
    use for bool
    """
    SCALAR = 10
    """
    all other scalar values, e.g. uuid
    """
    LEVEL_VERBOSE = 11
    LEVEL_DEBUG = 12
    LEVEL_INFORMATION = 13
    LEVEL_WARNING = 14
    LEVEL_ERROR = 15
    LEVEL_FATAL = 16



