from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from iot_protocols.devices.models import DeviceProfile, DeviceHardware


class Device(ABC):
    
    @property
    def device_id(self) -> str:
        """device_id
        Device identification. This must serves as a unique identifier among's all possible devices.
        """
        try:
            return str(self._id)
        except AttributeError:
            return
 
    @property
    def type(self) -> str:
        try:
            return self._type
        except AttributeError:
            return self.__class__.__name__

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @property
    def is_connected(self) -> bool:
        """is_connected returns if the device is connected or not. 

        Returns:
            bool: True if connection established, else False
        """
        try:
            return self._is_connected
        except AttributeError:
            return False
        
    @property
    def profile(self) -> DeviceProfile:
        return DeviceProfile(
            device_id=self.device_id,
            type=self.type,
            name=self.name
        )
        
    @property
    def name(self) -> str:
        """name 
        A Humand friendly name for this device.
        """
        try:
            return self._name
        except AttributeError:
            return f"{self.type} {self.device_id}" 
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def hardware(self) -> DeviceHardware:
        """hardware
        (optionnal) Return hardware info about this device.
        """
    
    @property
    def protocol(self) -> Any:
        """protocol Returns the protocol linked to this device.

        Returns:
            Any: Any Protocol instance
        """
    
    @abstractmethod
    def connect(self) -> None:
        """connect Connect to the device using apporpriate protocols.
        On connect, this instance must setup it's device profile and id.
        """
    
    @abstractmethod
    def disconnect(self) -> None:
        """disconnect Stop the communication between this instance and the device.
        This can be optionnal for some protocol.
        """
