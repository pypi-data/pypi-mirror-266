"""A basic utility designed to prettify and visualize fractions."""

import fractions
import re

__version__ = "2.0"
__description__ = "A basic utility designed to prettify and visualize fractions."
__author__ = "xyzpw"

def make_pretty(numerator, denominator, operation="", whole=None, hyphen=True) -> str:
    """Returns the string value to a prettified fraction.

    :param numerator:   numerator of the fraction
    :param denominator: denominator of the fraction
    :param whole:       the adjoining string of the fraction
    :param operation:   the operation connecting a whole value and fraction
    :param hyphen:      uses a hyphen-minus character in contrast to a horizontal bar vinculum"""
    vinculum = "-" if hyphen else "\u2015"
    numeratorLength = len(str(numerator))
    denominatorLength = len(str(denominator))
    if numeratorLength == denominatorLength:
        separatorLength = denominatorLength
        prettifiedFraction = f"{numerator}\n{vinculum*separatorLength}\n{denominator}"
    elif numeratorLength > denominatorLength:
        separatorLength = numeratorLength
        steps = (separatorLength - denominatorLength) // 2
        prettifiedFraction = f"{numerator}\n{vinculum*separatorLength}\n{' '*steps}{denominator}"
    elif numeratorLength < denominatorLength:
        separatorLength = denominatorLength
        steps = (separatorLength - numeratorLength) // 2
        prettifiedFraction = f"{' '*steps}{numerator}\n{vinculum*separatorLength}\n{denominator}"
    if whole != None:
        prettifiedFraction = f"{prettifiedFraction}\x1b[1A\r\x1b[{separatorLength}C {operation} {whole}\n"
    return prettifiedFraction

def visualize(*args, **kwargs):
    """Calls and prints the return value of `make_pretty` function."""
    print(make_pretty(*args, **kwargs))

def visualize_number(argNumber: int|float, hyphen=True):
    """Visualizes a rewritten fraction of a whole number."""
    if not isinstance(argNumber, float | int):
        raise ValueError("display value must be a number")
    argNumberInt = int(argNumber)
    argNumberDecimal = argNumber - argNumberInt
    if argNumberDecimal == 0:
        print(argNumber)
        return
    numberFraction = fractions.Fraction(argNumberDecimal).limit_denominator(1_000_000)
    regexFractionSearch = re.search(r"(?P<num>\d+)/(?P<den>\d+)", str(numberFraction))
    fracNumerator, fracDenominator = regexFractionSearch.group("num"), regexFractionSearch.group("den")
    prettifiedFraction = None
    if argNumberInt == 0:
        prettifiedFraction = make_pretty(fracNumerator, fracDenominator, hyphen=hyphen)
    elif argNumberInt > 0:
        prettifiedFraction = make_pretty(fracNumerator, fracDenominator, "+", argNumberInt, hyphen=hyphen)
    print(prettifiedFraction)

class Fraction:
    def __init__(self, numerator, denominator, operation="", whole=None, hyphen=True):
        self.numerator = numerator
        self.denominator = denominator
        self.operation = operation
        self.whole = whole
        self.hyphen = hyphen
    def __str__(self):
        return make_pretty(self.numerator, self.denominator, self.operation, self.whole, self.hyphen)
    def display(self):
        visualize(self.numerator, self.denominator, self.operation, self.whole, self.hyphen)
    def __repr__(self):
        return repr(self.__str__())
