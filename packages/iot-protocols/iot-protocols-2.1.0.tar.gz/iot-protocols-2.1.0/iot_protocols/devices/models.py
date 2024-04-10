from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class DeviceProfile:
    """
    device_id: unique identifier for this device.
    type: type of the device.
    name (optionnal): a name that represent this device. If not set will be a concatenation of type + device_id.
    """
    device_id: str = field()
    type: str = field(init=True)
    name: str = ""

    def __post_init__(self):
        if self.name == "":
            if self.type is None and self.device_id is None:
                self.name = f"Unknow Device"
            else:
                self.name = f"{self.type} {self.device_id}"

    def json(self) -> dict:
        return self.__dict__


@dataclass
class DeviceHardware:
    """
    serialNumber: serial number of the device.
    model: (optionnal) the model of the device
    revision (optionnal): the version of device hardware.
    """
    serialNumber: str = field(init=True)
    model: str = field(init=True, default="")
    revision: str = field(init=True, default="")

    def json(self) -> dict:
        return self.__dict__