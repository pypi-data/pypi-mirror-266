"""
Module that contains the ``scifloat`` class.
"""

from typing import NoReturn

from . import ConvertibleToFloat, ConvertibleToList
from .sciround import round_uncertainties, round_value


class scifloat:
    """
    Scientific variant of measurements with corresponding errors.
    Values are rounded based on their errors, which itself are
    rounded by scientific standards.

    Uncertainties are rounded to a given number of significant digits.
    Is the first number either a 1 or a 2 we round to two significant digits.
    Otherwise we round only to one significant digit. In any case it is rounded to
    the next number.

    >>> from scifloatpy.sciround import round_uncertainties,round_value
    >>> round_uncertainties(0.0513)
    0.06

    >>> round_uncertainties(1.2421)
    1.3

    Values are rounded to the number of digits of their error.
    >>> round_uncertainties(0.0102)
    0.011
    >>> round_value(1.36551315)
    1.366

    If the measuremnt has assymmetric errors, the one with the smallest precision, i.e.,
    the one with less digits.
    >>> round_uncertainties([0.0302,0.00891])
    [0.03,0.009]
    >>> round_value(1.36551315)
    1.37

    In such cases the other uncertainty needs also to be modified to the same precision.
    >>> 0.009
    0.01
    (Not implemented yet!)
    """

    def __new__(cls, __x: ConvertibleToFloat, __dx: ConvertibleToList) -> "scifloat":
        return super().__new__(cls)

    def __init__(self, __x: ConvertibleToFloat, __dx: ConvertibleToList) -> NoReturn:
        self.x = float(__x)
        if isinstance(__dx, (int, float)):
            self.dx = [__dx, __dx]
        elif isinstance(__dx, tuple):
            self.dx = list(__dx)
        else:
            self.dx = __dx
        self.rx = self.x
        self.rdx = self.dx.copy()
        self.sx = self.x
        self.sdx = self.dx.copy()

    def __str__(self) -> str:
        if self.sdx[0] == self.sdx[1]:
            return f"{self.sx} \u00b1 {self.sdx[0]}"
        return f"{self.sx} +{self.sdx[0]} | -{self.sdx[1]}"

    def __round__(self, ndigits: None = None) -> "scifloat":
        rdx = round_uncertainties(self.dx.copy())
        if any(list(map(lambda x: "." in x, rdx))):
            ndigits = min(map(lambda x: len(x.split(".")[-1]), rdx))
        else:
            ndigits = -max(map(lambda x: len(x) - len(x.rstrip("0")), rdx))

        rx = round_value(self.x, ndigits)
        self.rx = float(rx)
        self.rdx = list(map(float, rdx))
        self.sx = rx
        self.sdx = rdx
        print(self)
        return self
