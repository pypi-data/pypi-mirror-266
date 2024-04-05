from __future__ import annotations
import typing
import xad._xad.adj_1st
import xad._xad.fwd_1st
__all__ = ['abs', 'acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'cbrt', 'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'erf', 'erfc', 'exp', 'exp2', 'expm1', 'fabs', 'floor', 'fmax', 'fmin', 'fmod', 'frexp', 'ldexp', 'log', 'log10', 'log1p', 'log2', 'max', 'min', 'modf', 'nextafter', 'pow', 'radians', 'remainder', 'sin', 'sinh', 'smooth_abs', 'smooth_max', 'smooth_min', 'sqrt', 'tan', 'tanh', 'trunc']
@typing.overload
def abs(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    absolute value
    """
@typing.overload
def abs(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    absolute value
    """
@typing.overload
def abs(arg0: float) -> float:
    """
    absolute value
    """
@typing.overload
def acos(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    inverse cosine
    """
@typing.overload
def acos(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    inverse cosine
    """
@typing.overload
def acos(arg0: float) -> float:
    """
    inverse cosine
    """
@typing.overload
def acosh(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    inverse cosine hyperbolicus
    """
@typing.overload
def acosh(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    inverse cosine hyperbolicus
    """
@typing.overload
def acosh(arg0: float) -> float:
    """
    inverse cosine hyperbolicus
    """
@typing.overload
def asin(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    inverse sine
    """
@typing.overload
def asin(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    inverse sine
    """
@typing.overload
def asin(arg0: float) -> float:
    """
    inverse sine
    """
@typing.overload
def asinh(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    inverse sine hyperbolicus
    """
@typing.overload
def asinh(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    inverse sine hyperbolicus
    """
@typing.overload
def asinh(arg0: float) -> float:
    """
    inverse sine hyperbolicus
    """
@typing.overload
def atan(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    inverse tangent
    """
@typing.overload
def atan(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    inverse tangent
    """
@typing.overload
def atan(arg0: float) -> float:
    """
    inverse tangent
    """
@typing.overload
def atan2(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    4-quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    4 quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    4 quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    4-quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    4 quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    4 quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: float, arg1: float) -> float:
    """
    4-quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: float, arg1: float) -> float:
    """
    4 quadrant inverse tangent
    """
@typing.overload
def atan2(arg0: float, arg1: float) -> float:
    """
    4 quadrant inverse tangent
    """
@typing.overload
def atanh(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    inverse tangent hyperbolicus
    """
@typing.overload
def atanh(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    inverse tangent hyperbolicus
    """
@typing.overload
def atanh(arg0: float) -> float:
    """
    inverse tangent hyperbolicus
    """
@typing.overload
def cbrt(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    cubic root
    """
@typing.overload
def cbrt(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    cubic root
    """
@typing.overload
def cbrt(arg0: float) -> float:
    """
    cubic root
    """
@typing.overload
def ceil(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    rounding away from zero
    """
@typing.overload
def ceil(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    rounding away from zero
    """
@typing.overload
def ceil(arg0: float) -> float:
    """
    rounding away from zero
    """
@typing.overload
def copysign(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: float, arg1: float) -> float:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: float, arg1: float) -> float:
    """
    copy sign of one value to another
    """
@typing.overload
def copysign(arg0: float, arg1: float) -> float:
    """
    copy sign of one value to another
    """
@typing.overload
def cos(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    cosine
    """
@typing.overload
def cos(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    cosine
    """
@typing.overload
def cos(arg0: float) -> float:
    """
    cosine
    """
@typing.overload
def cosh(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    cosine hyperbolicus
    """
@typing.overload
def cosh(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    cosine hyperbolicus
    """
@typing.overload
def cosh(arg0: float) -> float:
    """
    cosine hyperbolicus
    """
@typing.overload
def degrees(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    convert radians to degrees
    """
@typing.overload
def degrees(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    convert radians to degrees
    """
@typing.overload
def degrees(arg0: float) -> float:
    """
    convert radians to degrees
    """
@typing.overload
def erf(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    error function
    """
@typing.overload
def erf(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    error function
    """
@typing.overload
def erf(arg0: float) -> float:
    """
    error function
    """
@typing.overload
def erfc(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    complementary error function
    """
@typing.overload
def erfc(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    complementary error function
    """
@typing.overload
def erfc(arg0: float) -> float:
    """
    complementary error function
    """
@typing.overload
def exp(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    exponential function
    """
@typing.overload
def exp(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    exponential function
    """
@typing.overload
def exp(arg0: float) -> float:
    """
    exponential function
    """
@typing.overload
def exp2(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    computes 2 to the power of the argument
    """
@typing.overload
def exp2(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    computes 2 to the power of the argument
    """
@typing.overload
def exp2(arg0: float) -> float:
    """
    computes 2 to the power of the argument
    """
@typing.overload
def expm1(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    computes exp(x)-1
    """
@typing.overload
def expm1(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    computes exp(x)-1
    """
@typing.overload
def expm1(arg0: float) -> float:
    """
    computes exp(x)-1
    """
@typing.overload
def fabs(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    absolute value
    """
@typing.overload
def fabs(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    absolute value
    """
@typing.overload
def fabs(arg0: float) -> float:
    """
    absolute value
    """
@typing.overload
def floor(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    rounding towards zero
    """
@typing.overload
def floor(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    rounding towards zero
    """
@typing.overload
def floor(arg0: float) -> float:
    """
    rounding towards zero
    """
@typing.overload
def fmax(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: float, arg1: float) -> float:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: float, arg1: float) -> float:
    """
    maximum of 2 values
    """
@typing.overload
def fmax(arg0: float, arg1: float) -> float:
    """
    maximum of 2 values
    """
@typing.overload
def fmin(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: float, arg1: float) -> float:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: float, arg1: float) -> float:
    """
    minimum of 2 values
    """
@typing.overload
def fmin(arg0: float, arg1: float) -> float:
    """
    minimum of 2 values
    """
@typing.overload
def fmod(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    floating point remainer after integer division
    """
@typing.overload
def fmod(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    floating point remainer after integer division
    """
@typing.overload
def fmod(arg0: float, arg1: float) -> float:
    """
    floating point remainer after integer division
    """
@typing.overload
def frexp(arg0: xad._xad.adj_1st.Real) -> tuple:
    """
    decomposes into normalised fraction and an integral power of 2
    """
@typing.overload
def frexp(arg0: xad._xad.fwd_1st.Real) -> tuple:
    """
    decomposes into normalised fraction and an integral power of 2
    """
@typing.overload
def frexp(arg0: float) -> tuple:
    """
    decomposes into normalised fraction and an integral power of 2
    """
@typing.overload
def ldexp(arg0: xad._xad.adj_1st.Real, arg1: int) -> xad._xad.adj_1st.Real:
    """
    mutiplies x by 2 to the power of exp
    """
@typing.overload
def ldexp(arg0: xad._xad.fwd_1st.Real, arg1: int) -> xad._xad.fwd_1st.Real:
    """
    mutiplies x by 2 to the power of exp
    """
@typing.overload
def ldexp(arg0: float, arg1: int) -> float:
    """
    mutiplies x by 2 to the power of exp
    """
@typing.overload
def log(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    natural logarithm
    """
@typing.overload
def log(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    natural logarithm
    """
@typing.overload
def log(arg0: float) -> float:
    """
    natural logarithm
    """
@typing.overload
def log10(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    base 10 logarithm
    """
@typing.overload
def log10(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    base 10 logarithm
    """
@typing.overload
def log10(arg0: float) -> float:
    """
    base 10 logarithm
    """
@typing.overload
def log1p(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    computes log(1 + x)
    """
@typing.overload
def log1p(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    computes log(1 + x)
    """
@typing.overload
def log1p(arg0: float) -> float:
    """
    computes log(1 + x)
    """
@typing.overload
def log2(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    base 2 logarithm
    """
@typing.overload
def log2(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    base 2 logarithm
    """
@typing.overload
def log2(arg0: float) -> float:
    """
    base 2 logarithm
    """
@typing.overload
def max(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: float, arg1: float) -> float:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: float, arg1: float) -> float:
    """
    maximum of 2 values
    """
@typing.overload
def max(arg0: float, arg1: float) -> float:
    """
    maximum of 2 values
    """
@typing.overload
def min(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: float, arg1: float) -> float:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: float, arg1: float) -> float:
    """
    minimum of 2 values
    """
@typing.overload
def min(arg0: float, arg1: float) -> float:
    """
    minimum of 2 values
    """
@typing.overload
def modf(arg0: xad._xad.adj_1st.Real) -> tuple:
    """
    decomposes into integral and fractional parts
    """
@typing.overload
def modf(arg0: xad._xad.fwd_1st.Real) -> tuple:
    """
    decomposes into integral and fractional parts
    """
@typing.overload
def modf(arg0: float) -> tuple:
    """
    decomposes into integral and fractional parts
    """
@typing.overload
def nextafter(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: float, arg1: float) -> float:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: float, arg1: float) -> float:
    """
    next representable value in the given direction
    """
@typing.overload
def nextafter(arg0: float, arg1: float) -> float:
    """
    next representable value in the given direction
    """
@typing.overload
def pow(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    power
    """
@typing.overload
def pow(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    power
    """
@typing.overload
def pow(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    power
    """
@typing.overload
def pow(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    power
    """
@typing.overload
def pow(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    power
    """
@typing.overload
def pow(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    power
    """
@typing.overload
def pow(arg0: float, arg1: float) -> float:
    """
    power
    """
@typing.overload
def pow(arg0: float, arg1: float) -> float:
    """
    power
    """
@typing.overload
def pow(arg0: float, arg1: float) -> float:
    """
    power
    """
@typing.overload
def radians(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    convert degrees to radians
    """
@typing.overload
def radians(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    convert degrees to radians
    """
@typing.overload
def radians(arg0: float) -> float:
    """
    convert degrees to radians
    """
@typing.overload
def remainder(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: float, arg1: float) -> float:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: float, arg1: float) -> float:
    """
    signed remainder after integer division
    """
@typing.overload
def remainder(arg0: float, arg1: float) -> float:
    """
    signed remainder after integer division
    """
@typing.overload
def sin(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    sine
    """
@typing.overload
def sin(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    sine
    """
@typing.overload
def sin(arg0: float) -> float:
    """
    sine
    """
@typing.overload
def sinh(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    sine hyperbolicus
    """
@typing.overload
def sinh(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    sine hyperbolicus
    """
@typing.overload
def sinh(arg0: float) -> float:
    """
    sine hyperbolicus
    """
@typing.overload
def smooth_abs(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    smoothed abs function for well-defined derivatives
    """
@typing.overload
def smooth_abs(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    smoothed abs function for well-defined derivatives
    """
@typing.overload
def smooth_abs(arg0: float) -> float:
    """
    smoothed abs function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: float, arg1: float) -> float:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: float, arg1: float) -> float:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_max(arg0: float, arg1: float) -> float:
    """
    smoothed max function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: xad._xad.adj_1st.Real, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: xad._xad.adj_1st.Real, arg1: float) -> xad._xad.adj_1st.Real:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: float, arg1: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: xad._xad.fwd_1st.Real, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: xad._xad.fwd_1st.Real, arg1: float) -> xad._xad.fwd_1st.Real:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: float, arg1: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: float, arg1: float) -> float:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: float, arg1: float) -> float:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def smooth_min(arg0: float, arg1: float) -> float:
    """
    smoothed min function for well-defined derivatives
    """
@typing.overload
def sqrt(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    square root
    """
@typing.overload
def sqrt(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    square root
    """
@typing.overload
def sqrt(arg0: float) -> float:
    """
    square root
    """
@typing.overload
def tan(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    tangent
    """
@typing.overload
def tan(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    tangent
    """
@typing.overload
def tan(arg0: float) -> float:
    """
    tangent
    """
@typing.overload
def tanh(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    tangent hyperbolicus
    """
@typing.overload
def tanh(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    tangent hyperbolicus
    """
@typing.overload
def tanh(arg0: float) -> float:
    """
    tangent hyperbolicus
    """
@typing.overload
def trunc(arg0: xad._xad.adj_1st.Real) -> xad._xad.adj_1st.Real:
    """
    cut off decimals
    """
@typing.overload
def trunc(arg0: xad._xad.fwd_1st.Real) -> xad._xad.fwd_1st.Real:
    """
    cut off decimals
    """
@typing.overload
def trunc(arg0: float) -> float:
    """
    cut off decimals
    """
