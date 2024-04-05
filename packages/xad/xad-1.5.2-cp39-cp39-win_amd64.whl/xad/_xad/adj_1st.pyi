from __future__ import annotations
import typing
__all__ = ['Real', 'Tape']
class Real:
    """
    active arithmetic type for first order adjoint mode
    """
    __hash__: typing.ClassVar[None] = None
    def __abs__(self) -> Real:
        ...
    @typing.overload
    def __add__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __add__(self, arg0: Real) -> Real:
        ...
    def __bool__(self) -> bool:
        ...
    def __ceil__(self) -> int:
        ...
    @typing.overload
    def __divmod__(self, arg0: Real) -> tuple[Real, Real]:
        ...
    @typing.overload
    def __divmod__(self, arg0: float) -> tuple[Real, Real]:
        ...
    @typing.overload
    def __divmod__(self, arg0: int) -> tuple[Real, Real]:
        ...
    @typing.overload
    def __eq__(self, arg0: Real) -> bool:
        ...
    @typing.overload
    def __eq__(self, arg0: float) -> bool:
        ...
    def __floor__(self) -> int:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __floordiv__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __floordiv__(self, arg0: int) -> Real:
        ...
    @typing.overload
    def __ge__(self, arg0: Real) -> bool:
        ...
    @typing.overload
    def __ge__(self, arg0: float) -> bool:
        ...
    @typing.overload
    def __gt__(self, arg0: Real) -> bool:
        ...
    @typing.overload
    def __gt__(self, arg0: float) -> bool:
        ...
    @typing.overload
    def __init__(self, arg0: float) -> None:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    def __int__(self) -> int:
        ...
    @typing.overload
    def __le__(self, arg0: Real) -> bool:
        ...
    @typing.overload
    def __le__(self, arg0: float) -> bool:
        ...
    @typing.overload
    def __lt__(self, arg0: Real) -> bool:
        ...
    @typing.overload
    def __lt__(self, arg0: float) -> bool:
        ...
    @typing.overload
    def __mod__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __mod__(self, arg0: int) -> Real:
        ...
    @typing.overload
    def __mod__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __mul__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __mul__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __ne__(self, arg0: Real) -> bool:
        ...
    @typing.overload
    def __ne__(self, arg0: float) -> bool:
        ...
    def __neg__(self) -> Real:
        ...
    def __pos__(self) -> Real:
        ...
    @typing.overload
    def __pow__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __pow__(self, arg0: int) -> Real:
        ...
    @typing.overload
    def __pow__(self, arg0: float) -> Real:
        ...
    def __radd__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __rdivmod__(self, arg0: Real) -> tuple[Real, Real]:
        ...
    @typing.overload
    def __rdivmod__(self, arg0: float) -> tuple[Real, Real]:
        ...
    @typing.overload
    def __rdivmod__(self, arg0: int) -> tuple[Real, Real]:
        ...
    def __repr__(self) -> str:
        ...
    def __req__(self, arg0: float) -> bool:
        ...
    @typing.overload
    def __rfloordiv__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __rfloordiv__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __rfloordiv__(self, arg0: int) -> Real:
        ...
    def __rge__(self, arg0: float) -> bool:
        ...
    def __rgt__(self, arg0: float) -> bool:
        ...
    def __rle__(self, arg0: float) -> bool:
        ...
    def __rlt__(self, arg0: float) -> bool:
        ...
    @typing.overload
    def __rmod__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __rmod__(self, arg0: int) -> Real:
        ...
    @typing.overload
    def __rmod__(self, arg0: float) -> Real:
        ...
    def __rmul__(self, arg0: float) -> Real:
        ...
    def __rne__(self, arg0: float) -> bool:
        ...
    @typing.overload
    def __round__(self, arg0: int) -> Real:
        ...
    @typing.overload
    def __round__(self) -> int:
        ...
    @typing.overload
    def __rpow__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __rpow__(self, arg0: int) -> Real:
        ...
    @typing.overload
    def __rpow__(self, arg0: float) -> Real:
        ...
    def __rsub__(self, arg0: float) -> Real:
        ...
    def __rtruediv__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __sub__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __sub__(self, arg0: Real) -> Real:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> Real:
        ...
    @typing.overload
    def __truediv__(self, arg0: Real) -> Real:
        ...
    def __trunc__(self) -> int:
        ...
    def conjugate(self) -> Real:
        """
        complex conjugate
        """
    def getDerivative(self) -> float:
        """
        get the adjoint of this variable
        """
    def getSlot(self) -> int:
        """
        Get the slot of this variable on the tape
        """
    def getValue(self) -> float:
        """
        get the underlying value
        """
    def imag(self) -> Real:
        """
        imaginary part
        """
    def real(self) -> Real:
        """
        real part
        """
    def setAdjoint(self, arg0: float) -> None:
        """
        set adjoint of this variable
        """
    def setDerivative(self, arg0: float) -> None:
        """
        set the adjoint of this variable
        """
    def shouldRecord(self) -> bool:
        """
        Check if the variable is registered on tape and should record
        """
class Tape:
    @staticmethod
    def getActive() -> Tape:
        """
        class method to get a reference to the currently active tape
        """
    def __enter__(self) -> Tape:
        """
        enters a context `with tape`, activating the tape
        """
    def __exit__(self, arg0: type | None, arg1: typing.Any | None, arg2: typing.Any | None) -> None:
        """
        deactivates the tape when exiting the context
        """
    def __init__(self) -> None:
        """
        constructs a tape without activating it
        """
    def activate(self) -> None:
        """
        activate the tape
        """
    def clearAll(self) -> None:
        """
        clear/reset the tape completely, without de-allocating memory. Should be used for re-using the tape, rather than creating a new one
        """
    def clearDerivatives(self) -> None:
        """
        clear all derivatives stored on the tape
        """
    def clearDerivativesAfter(self, arg0: int) -> None:
        """
        clear all derivatives after the given position
        """
    def computeAdjoints(self) -> None:
        """
        Roll back the tape until the point of calling `newRecording`, propagating adjoints from outputs to inputs
        """
    def computeAdjointsTo(self, arg0: int) -> None:
        """
        Roll back the tape until the given position (see `getPosition`), propagating adjoints from outputs backwards.
        """
    def deactivate(self) -> None:
        """
        deactivate the tape
        """
    @typing.overload
    def derivative(self, arg0: Real) -> float:
        """
        get the slot of the given variable
        """
    @typing.overload
    def derivative(self, arg0: int) -> float:
        """
        get the derivative stored at the given slot position
        """
    @typing.overload
    def getDerivative(self, arg0: Real) -> float:
        """
        alias for `derivative`
        """
    @typing.overload
    def getDerivative(self, arg0: int) -> float:
        """
        alias for `derivative`
        """
    def getMemory(self) -> int:
        """
        Get the total memory consumed by the tape in bytes
        """
    def getPosition(self) -> int:
        """
        get the current position on the tape. Used in conjunction with `computeAdjointsTo`.
        """
    def isActive(self) -> bool:
        """
        check if the tape is active
        """
    def newRecording(self) -> None:
        """
        Start a new recording on tape, marking the start of a function to be derived
        """
    def printStatus(self) -> None:
        """
        output the status of the tape (for debugging/information)
        """
    def registerInput(self, arg0: Real) -> None:
        """
        registers an input variable with tape, for recording
        """
    def registerOutput(self, arg0: Real) -> None:
        """
        registers an output with the tape (to be called before setting output adjoints)
        """
    def resetTo(self, arg0: int) -> None:
        """
        reset the tape back to the given position
        """
    @typing.overload
    def setDerivative(self, arg0: Real, arg1: float) -> None:
        """
        sets the derivative of the given active variable to the value given
        """
    @typing.overload
    def setDerivative(self, arg0: int, arg1: float) -> None:
        """
        sets the derivative at the given slot to the given value
        """
