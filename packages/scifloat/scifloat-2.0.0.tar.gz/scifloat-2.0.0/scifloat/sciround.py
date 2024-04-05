"""
Module with the two methods to round the scientific float.

Example
-------
>>> round_uncertainties([0.124,0.201])
    [0.13,0.21]

>>> round_value(1.235511,2)
    1.24
"""

import decimal
import math

from . import ConvertibleToFloat, ConvertibleToList

__all__ = [n for n in globals() if n[0] != "_"]


def _float_to_str(__x: ConvertibleToFloat):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    dcx = decimal.Context()
    dcx.prec = 30
    d1 = dcx.create_decimal(repr(__x))
    return format(d1, "f")


def _order_of_magnitude(__x: ConvertibleToFloat):
    if __x == 0:
        return __x
    return math.floor(math.log(__x, 10))


def _significant_numbers(__x: ConvertibleToFloat):
    __s = _float_to_str(__x)
    if __s[0] in ["1", "2"]:
        return 2
    return 1


def _sci_round(__x: ConvertibleToFloat, __sig_num: int):
    __s: str = _float_to_str(__x)
    if len(__s.replace(".", "")) == __sig_num:
        return float(__s)
    if __s == "0":
        return 0
    if __sig_num == 2:
        if not __s[3] == "0":
            return float(__s[:3]) + 0.1
        return float(__s[:3])
    else:
        if not __s[2] == "0":
            return int(__s[:1]) + 1
        return int(__s[:1])


def _number_to_str(__x, __sig_num, __magnitude):
    __s = _float_to_str(__x)
    nmod = __s.replace(".", "")
    nmod = nmod.lstrip("0")
    nmod = nmod.rstrip("0")
    if len(nmod) < __sig_num:
        return __s + "0"
    if len(nmod) > __sig_num:
        return _float_to_str(round(__x, -__magnitude + 1))
    return __s


def _round_uncertainty(__x):
    mag = _order_of_magnitude(__x)
    xflat = __x * 10**-mag
    nsig = _significant_numbers(xflat)
    xround = _sci_round(xflat, nsig)
    xround = xround * 10**mag
    if mag > 0:
        xround = int(xround)
    return _number_to_str(xround, nsig, mag)


def round_uncertainties(__dx: ConvertibleToList) -> list:
    """
    Returns the, by Scientific rules, rounded uncertainties.
    """
    if isinstance(__dx, (int, float)):
        __dx = [__dx, __dx]
    if isinstance(__dx, tuple):
        __dx = list(__dx)
    for i, dx in enumerate(__dx):
        __dx[i] = _round_uncertainty(dx)
    return __dx


def round_value(__x: ConvertibleToFloat, __ndigits: int) -> float:
    """
    Returns the, by Scientific rules, rounded value.

    Examples
    -------
    >>> round_value(1.25,1)
    1.2

    >>> round_value(1.315,2)
    1.32
    """
    # need to remove computation bug with floating points
    if not __ndigits < 0:
        __x = math.floor(__x * 10 ** (__ndigits + 1)) / 10 ** (__ndigits + 1)
        # even rounding, i.e., statistically correct
        return round(__x * 10**__ndigits) / 10**__ndigits
    return round(int(__x), __ndigits)
