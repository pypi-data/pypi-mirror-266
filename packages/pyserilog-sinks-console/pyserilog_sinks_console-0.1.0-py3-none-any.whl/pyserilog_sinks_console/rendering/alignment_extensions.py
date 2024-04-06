from pyserilog.parsing.alignment import Alignment


def widen(alignment: Alignment, amount: int):
    return Alignment(alignment.direction, alignment.width + amount)
