from __future__ import annotations
__all__ = ['DerivativesNotInitialized', 'NoTapeException', 'OutOfRange', 'TapeAlreadyActive', 'XadException']
class DerivativesNotInitialized(XadException):
    """
    Raised when setting derivatives on the tape without a recording and registered outputs
    """
class NoTapeException(XadException):
    """
    raised if an opteration that requires an active tape is performed while not tape is active
    """
class OutOfRange(XadException):
    """
    raised when setting a derivative at a slot that is out of range of the recorded variables
    """
class TapeAlreadyActive(XadException):
    """
    Raised when activating a tape when this or another tape is already active in the current thread
    """
class XadException(Exception):
    """
    Base class for all exceptions raised by XAD
    """
