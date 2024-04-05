"""
Python bindings for the XAD comprehensive library for automatic differentiation
"""
from __future__ import annotations
from xad._xad import adj_1st
from xad._xad import fwd_1st
from . import _xad
__all__: list = ['value', 'derivative']
def derivative(x: typing.Union[xad._xad.adj_1st.Real, xad._xad.fwd_1st.Real]) -> float:
    """
    Get the derivative of an XAD active type - forward or adjoint mode
    
        Args:
            x (Real): Argument to extract the derivative information from
    
        Returns:
            float: The derivative
        
    """
def value(x: typing.Union[xad._xad.adj_1st.Real, xad._xad.fwd_1st.Real, typing.Any]) -> float:
    """
    Get the value of an XAD active type - or return the value itself otherwise
    
        Args:
            x (Real | any): Argument to get the value of
    
        Returns:
            float: The value stored in the variable
        
    """
