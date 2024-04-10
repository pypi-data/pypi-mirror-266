from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from iot_protocols.data import RelayState, IOState, Serie


class Relay(ABC):

    @abstractmethod
    def read_relay(self) -> RelayState:
        """ Read current Relay State"""

    @abstractmethod
    def set_relay(self, value: RelayState) -> None:
        """ Set the current relay state value """


class RelayArray(ABC):

    @abstractmethod
    def read_relay_array(self) -> List[RelayState]:
        """ Read the relay array values """

    @abstractmethod
    def set_relay_array(self, value: List[RelayState]) -> None:
        """ Set the current relay array state """


class IO(ABC):

    @abstractmethod
    def read_io(self):
        """ Must read IO state """


class IOArray(ABC):

    @abstractmethod
    def read_io_array(self) -> List[IOState]:
        """ Read the current io array """



class EnergyMeter(ABC):

    @abstractmethod
    def read_energy(self, **kwargs) -> None:
        """
        Read and update the energy measures from the meter.
        The status of the meter and attribute must be updated accordingly after that.
        """

        
class SinglePhaseEnergyMeter(EnergyMeter):
        
        def __init__(self) -> None:
            self.content = {}
        
        def __getitem__(self, key: str) -> Serie:
            return self.content.get(key, None)
        
        def __setitem__(self, key: str, value: dict | Serie) -> None:
            if not isinstance(value, dict) and not isinstance(value, Serie):
                raise ValueError(f"Invalid Value, must be dict or Serie, got : {type(value)}")
            
            if isinstance(value, dict):
                value = Serie(**value)
            self.content[key] = value

        @property
        def Ap(self) -> Serie:
            return self["Ap"]
        
        @property
        def Am(self) -> Serie:
            return self["Am"]
    
        @property
        def Ap_old(self) -> Serie:
            return self["Ap_old"]
    
        @property
        def Am_old(self) -> Serie:
            return self["Am_old"]

        @property
        def Qp(self) -> Serie:
            return self["Qp"]

        @property
        def Qm(self) -> Serie:
            return self["Qm"]

        @property
        def Pp(self) -> Serie:
            return self["Pp"]

        @property
        def Pm(self) -> Serie:
            return self["Pm"]

        
class ThreePhasesEnergyMeter(EnergyMeter):
    def read_energy(self, **kwargs) -> None:
        pass

    class Line:
        def __init__(self) -> None:
            self.content = {}
        
        def __getitem__(self, key: str) -> Serie:
            return self.content.get(key, None)
        
        def __setitem__(self, key: str, value: dict | Serie) -> None:
            if not isinstance(value, dict) and not isinstance(value, Serie):
                raise ValueError(f"Invalid Value, must be dict or Serie, got : {type(value)}")
            
            if isinstance(value, dict):
                value = Serie(**value)
            self.content[key] = value

        @property
        def Ap(self) -> Serie:
            return self["Ap"]
        
        @property
        def Am(self) -> Serie:
            return self["Am"]

        @property
        def Qp(self) -> Serie:
            return self["Qp"]

        @property
        def Qm(self) -> Serie:
            return self["Qm"]

        @property
        def Pp(self) -> Serie:
            return self["Pp"]

        @property
        def Pm(self) -> Serie:
            return self["Pm"]

        def json(self) -> dict:
            return {k: v.json() for k,v in self.content.items()}

    def __init__(self) -> None:
        self.content = {
            "L1": self.Line(),
            "L2": self.Line(),
            "L3": self.Line(),
        }

    def __getitem__(self, key: str) -> Serie | Line:
        return self.content.get(key, None)

    def __setitem__(self, key: str, value: dict | Serie | Line) -> None:
        if not isinstance(value, dict) and not isinstance(value, Serie):
                raise ValueError(f"Invalid Value, must be dict or Serie, got : {type(value)}")
        
        if isinstance(value, dict):
                value = Serie(**value)

        splited = key.split(".")
        if len(splited) == 1:
            self.content[splited[0]] = value
            
        elif len(splited) == 2:
            self.content[splited[0]][splited[1]] = value
 
    @property
    def Ap(self) -> Serie:
        return self["Ap"]
    
    @property
    def Am(self) -> Serie:
        return self["Am"]
    
    @property
    def Ap_old(self) -> Serie:
        return self["Ap_old"]

    @property
    def Am_old(self) -> Serie:
        return self["Am_old"]
    
    @property
    def Qp(self) -> Serie:
        return self["Qp"]

    @property
    def Qm(self) -> Serie:
        return self["Qm"]

    @property
    def P(self) -> Serie:
        return self["P"]

    @property
    def R(self) -> Serie:
        return self["R"]

    @property
    def Pp(self) -> Serie:
        return self["Pp"]

    @property
    def Pm(self) -> Serie:
        return self["Pm"]
    
    @property
    def L1(self) -> Line:
        return self["L1"]
    
    @property
    def L2(self) -> Line:
        return self["L2"]
    
    @property
    def L3(self) -> Line:
        return self["L3"]
    
    def json(self) -> dict:
        return {k: v.json() for k,v in self.content.items()}
