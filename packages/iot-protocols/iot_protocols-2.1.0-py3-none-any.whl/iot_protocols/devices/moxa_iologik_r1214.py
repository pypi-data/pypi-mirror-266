import logging
from typing import List

from iot_protocols.data import IOState, RelayState
from iot_protocols.devices.interfaces import RelayArray, IOArray
from iot_protocols.devices.basics import Device
from iot_protocols.devices.models import DeviceHardware, DeviceProfile
from iot_protocols.protocols.modbus.client import ModbusClient
from iot_protocols.protocols.modbus.decoder import ModbusPayloadDecoder
from iot_protocols.protocols.modbus import exceptions, requests


class MoxaIoLogikR1214(Device, RelayArray, IOArray):

    def __init__(self,
                 modbus_id: int,
                 port: str,
                 baudrate: int=9600,
                 parity: str="N",
                 bytesize: int=8,
                 stopbits: int=1,
                 timeout: int=5,
                 **kwargs) -> None:
            self._client = ModbusClient.with_serial_client(
                port=port,
                method="rtu",
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout
            )
            self._modbus_id = modbus_id

    def connect(self) -> None:
        self._client.connect()
        self._read_serial_number_and_model_info()
        self._is_connected = True

    def disconnect(self) -> None:
        self._client.disconnect()
    
    def _read_serial_number_and_model_info(self) -> None:
        if not hasattr(self, "_serial_number") or not hasattr(self, "_model"):
            with self._client as client:
                self._serial_number = client.request(
                    requests.ReadInputRegister(
                        address=0x754B,
                        count=6,
                        unit=self._modbus_id,
                        encoding="str"
                    )
                )
                self._model = client.request(
                    requests.ReadInputRegister(
                        address=0x7555,
                        count=10,
                        unit=self._modbus_id,
                        encoding="str"
                    )
                )
        self._id = self._serial_number
    
    @property
    def hardware(self) -> DeviceHardware:
        return DeviceHardware(
             serialNumber=self._serial_number,
             model=self._model
        )

    def read_io_array(self) -> List[IOState]:
        with self._client as client:
            result = client.request(
                requests.ReadDiscreteInput(
                    address=0x000,
                    count=6,
                    unit=self._modbus_id
                )
            )

        if result is None:
            raise TimeoutError(f"Timeout while trying to read moxa IOs.")
        
        ios = [IOState(int(io)) for io in result]
        return ios
    
    def read_relay(self, relay_index: int=0) -> RelayState:
        with self._client as client:
            result = client.request(
                requests.ReadCoils(
                    address=0x0140 + relay_index,
                    count=1,
                    unit=self._modbus_id
                )
            )
        
        if result is None:
            raise TimeoutError(f"Timeout while trying to read moxa Relays.")
        
        relay = RelayState(int(result))
        return relay

    
    def set_relay(self, value: RelayState, relay_index: int=0) -> None:
        if not isinstance(value, (RelayState, str)):
            raise ValueError(f"Wrong values for setting relays arrays : {value}. Must be either 'OPEN', 'CLOSED' or RelayState.")

        if isinstance(value, str):
            if value not in ["CLOSED", "OPEN"]:
                raise ValueError(f"Value must be 'OPEN' or 'CLOSED', not {value}")
            value = RelayState.from_string(value)
    
        
        with self._client as client:
            result = client.request(
                requests.WriteCoils(
                    address=0x0140 + relay_index,
                    values=[value.value],
                    unit=self._modbus_id
                )
            )
    
            if result is None:
                raise TimeoutError(f"Timeout while trying to set moxa Relay.")
        
    def read_relay_array(self) -> List[RelayState]:
        with self._client as client:
            result = client.request(
                requests.ReadCoils(
                    address=0x0140,
                    count=6,
                    unit=self._modbus_id
                )
            )
        
            if result is None:
                raise TimeoutError(f"Timeout while trying to read moxa Relays.")
            
            relays = [RelayState(int(io)) for io in result]
            return relays
        

    def set_relay_array(self, value: List[RelayState]) -> None:
        
        if not isinstance(value, list) \
        and not isinstance(value[0], (RelayState, str)):
            raise ValueError(f"Wrong values for setting relays arrays : {value}.")

        if isinstance(value[0], str):
            if value[0] is not "OPEN" or value[0] is not "CLOSED":
                raise ValueError(f"Value must be 'OPEN' or 'CLOSED', not {value[0]}")
            value = [RelayState.from_string(val) for val in value]
        
        with self._client as client:
            result = client.request(
                requests.WriteCoils(
                    address=0x0140,
                    values=[val.value for val in value],
                    unit=self._modbus_id
                )
            )
        
            if result is None:
                raise TimeoutError(f"Timeout while trying to set moxa Relays.")
            
        