"""
--------------------------------------------------------------------------------
                                MODELS
--------------------------------------------------------------------------------
"""
from __future__ import annotations

from dataclasses import dataclass, field
import datetime
from enum import Enum
from typing import Any, List


"""----------------------------- Data Elements ------------------------------"""

class IOState(int, Enum):
    """IOState Indicates the state of any kind of digital input.
    ..attribute:: LOW 
    Indicates that this IO is int it's low value state (False)

    ..attribute:: HIGH
    Indicates that this IO is in it's high value state (True).
    """

    HIGH = 1
    LOW = 0

    @classmethod
    def from_string(cls, value: str) -> Any:
        return cls(getattr(cls, value))
    
    
class RelayState(int, Enum):
    """RelayState Indicates the state of any kind of relay.
    ..attribute:: OPEN 
    the relay is open and no current flows to it.

    ..attribute:: CLOSED
    The relay is closed an current can flow to it.
    """
    OPEN = 0
    CLOSED = 1

    @classmethod
    def from_string(cls, value: str) -> Any:
        return cls(getattr(cls, value))
    
    def to_string(self) -> str:
        return self.name
    

@dataclass
class Serie:
    """ 
    name (str): name of this serie
    value (int | float): value of the serie
    unit (str, optional): Unit associated to the value. Defaults to None.
    """
    name: str
    value: int | float
    unit: str = field(default=None)

    def json(self) -> dict:
        """json return a json representation of this serie.
        Returns:
            dict: dict representing the serie.
        """
        return {
            self.name: {
                "value": self.value,
                "unit": self.unit
            }
        }
