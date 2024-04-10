"""
IEC 62056 (serial/tcp) module.
This module allows to exchange data using the IEC62056 protocol over a serial line.
* How to use : 
    1) create a client : client = SerialClient(baudrate=xxx, port="xxx", ...)
    2) client.connect()
    3) read all or registers : client.request(device_address, table, timeout)
"""
from __future__ import annotations
from dataclasses import dataclass, field

import logging
import time
import serial
from serial.serialutil import SerialException

from typing import List

from iot_protocols.protocols.iec62056.tools import client, messages, constants, exceptions

from iot_protocols.protocols.iec62056.exceptions import *
from iot_protocols.protocols.iec62056.exceptions import IEC62056RequestException, MeterIdentificationFailed, SerialPortBusyException


IEC62056_REACTION_TIME = 1.5 # Maximum reaction time for IEC62056


@dataclass
class TariffResponse:
    data: List[messages.DataSet]
    bcc: bytes
    checked: bool = field(default=False)

    def __repr__(self) -> str:
        return f"Tariff Response (number of datasets : {len(self.data)})(bcc: {self.checked})"

    def get_register(self, address: str) -> messages.DataSet:
        for dataset in self.data:
            if dataset.address == address:
                return dataset

class AckStopResponse(messages.CommandMessage):
    
    @classmethod
    def from_representation(cls, string_data):
        _message = string_data[:-1]  # remove bcc
        header = _message[:3]
        body = _message[3:]

        command = header[1]
        command_type = int(header[2])

        return cls(command, command_type, None)
    
class SerialClient:
    
    """Class to communicate with meter using IEC62056-21 protocol.
    Usage:
    - Create a new client specifying it's baudrate, the port, if needed the meter address (serial number, ..) and the type of client (serial, tcp (encapsulated), ..).
    - To request all dataset available use client.read_all()
    - To request a particular register use client.read_registers(list_of_registers_by_obis_code).

    Returns:
        client : A new instance of a IEC62056 client's.
    """
    BAUDRATE_CHAR = {
        300: "0",
        600: "1",
        1200: "2",
        2400: "3",
        4800: "4",
        9600: "5",
        19200: "6"
    }

    def __init__(
            self,
            baudrate: int,
            port: str,
            parity: str,
            bytesize: int,
            stopbits: int,
            **kwargs):
        
        self._baudrate = baudrate
        self._port = port
        self._parity = parity
        self._bytesize = bytesize
        self._stopbits = stopbits

        self._client: client.Iec6205621Client = client.Iec6205621Client.with_serial_transport(
            port=self._port,
            device_address=""
        )

        self._client.transport.TRANSPORT_REQUIRES_ADDRESS = True

    def __enter__(self) -> SerialClient:
        self.connect()
        return self
    
    def __exit__(self, *args) -> None:
        self.disconnect()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(baudrate : {self._baudrate} | port: {self._port} | {self._parity} | {self._bytesize} | {self._stopbits})"
    
    @property
    def baudrate(self) -> int:
        try:
            return self._client.transport.port.baudrate
        except AttributeError:
            return "undefined"
    
    def connect(self):
        try:
            if not self._is_connected():
                self._client.connect()
            
            self._client.transport.port.baudrate = self._baudrate

        except serial.serialutil.SerialException as err:
            raise SerialPortBusyException(f"The serial port {self._port} is not available : {err}")
        
    def _is_connected(self) -> bool:
        if self._client.transport.port is not None:
            return self._client.transport.port.is_open
        return False
    
    def disconnect(self):
        self._client.disconnect()

    def request(self, meter_address: str="", table: int=0, timeout: int = 30) -> TariffResponse:
        """read_registers specified in the list for the requested table of the iec62056-21 meter.

        Args:
            registers (list, optional): list of registers obis code to read. Defaults to [].
            table (str, optional): table to be read. Defaults to 0 which is equivalent to a standart readout.

        Returns:
            List[messages.DataSet]: A list of Dataset element that contains the requested registers if found.
        """
        try:
            logging.debug(f"[Meter.Identification] Start Identification Message.")
            identification = self.read_tariff_identification(device_address=meter_address)
            logging.debug(f"[Meter.Identification] Meter Identification has been read : {identification}")
            
            self._send_ack_message(table=table)

            logging.debug(f"[Meter.ACK.Sent] ACK message.")
            response: TariffResponse = self.read_tariff_response(timeout=timeout)
            logging.debug(f"[Meter.Data.Received] Response from tariff device : {response!r}")

            return response

        except Exception as err:
            if type(err) == SerialException:
                raise IEC62056RequestException(f"The communication port has failed : {err}")
            else:
                logging.error(f"Error during the request : {err}")

    def read_tariff_identification(self, device_address: str="", ack_stop: bool=False):
        try:
            request = messages.RequestMessage(device_address=device_address)
            logging.debug(f"[Identification.Request] Sending identification request: {request}.")
            self._client.transport.send(request.to_bytes())
        except TimeoutError as err:
            raise TimeoutError(f"Reading meter's identification timeouted : {err}")
        
        # Wait to ensure the tariff device has time to responds.
        self._client.rest(IEC62056_REACTION_TIME)

        response = self._client.read_identification()
        if isinstance(response, messages.IdentificationMessage):
            logging.debug(f"[Identification.Response] Received : {response}")
            if ack_stop:
                logging.debug(f"Sending ACK stop to end tariff exchange...")
                self._send_ack_stop()
                stop_ack_response = self._read_ack_stop_response()
                logging.debug(f"ACK Response from tariff device : {stop_ack_response}")
                if isinstance(stop_ack_response, AckStopResponse):
                    return response
                else:
                    logging.warning("Tariff device did not return ACK STOP message back !")

            return response
        else:
            self._send_ack_stop()
            raise MeterIdentificationFailed(f"Invalid message identification. (COM set with : {self.baudrate} | {self._parity} | {self._bytesize} | {self._stopbits})")
        
    def _get_ack_message(self, table: int=0) -> messages.AckOptionSelectMessage:
        message = messages.AckOptionSelectMessage(
            baud_char=self.BAUDRATE_CHAR[self._baudrate],
            mode_char=table
        )

        return message

    def _send_ack_message(self, table: int=0) -> None:
        message = self._get_ack_message(table)
        data = message.to_bytes()
        self._client.transport.send(data)
        self._client.rest(IEC62056_REACTION_TIME)

    def _send_ack_stop(self) -> None:
        message = messages.AckOptionSelectMessage("", "")
        data = message.to_bytes()
        self._client.transport.send(data)
        self._client.rest(IEC62056_REACTION_TIME)

    def _read_ack_stop_response(self) -> AckStopResponse:
        serial_client : serial.Serial = self._client.transport.port
        serial_client.timeout = 2.2
        data = serial_client.read_until(constants.ETX.encode())
        data += serial_client.read()
        return AckStopResponse.from_bytes(data)
    
    @staticmethod
    def check_bcc(data: bytes, bcc: bytes) -> bool:
        if not isinstance(data, bytes) or not isinstance(bcc, bytes) or len(bcc) != 1:
            raise ValueError("Input must be bytes and bcc must be a single byte")
        x = b'\x00'[0]
        for b in data[1:]:
            x = x^b

        logging.debug(f"[BCC.Check] received({bcc[0]}) | computed({x})")
        return x == bcc[0]

    def read_tariff_response(self, timeout: int = 30) -> TariffResponse:
        """read_tariff_response Read the serial buffer and parse the tariff device response.
        This stop when the ETX end of frame char is read or if the timeout is reached.

        Args:
            timeout (int, optional): Maximum time to read the response. Defaults to 15.

        Returns:
            TariffResponse: _description_
        """
        result = []
        port: serial.Serial = self._client.transport.port
        port.timeout = timeout
        start = time.perf_counter()
        encoded = port.read_until(constants.ETX.encode())
        if (time.perf_counter() - start) > timeout:
            self._send_ack_stop()
            raise TimeoutError(f"Timeout exceed for this request ! ")

        bcc = port.read(1)
        bcc_checked = self.check_bcc(encoded, bcc)

        logging.debug(f"[Meter.ReadTariffResponse.Received] Received {len(encoded)} bytes (bcc: {bcc}).")

        lines = encoded.decode().split('\r\n')

        for line in lines:
            try:
                # The first line contains STX character that can be removed for decoding first register.
                if line.startswith(constants.STX):
                    line = line.replace(constants.STX, '')

                if line.startswith(constants.ETX):
                    line = line.replace(constants.ETX, '')
              
                try:
                    dataset = messages.DataSet.from_representation(line)
                    result.append(dataset)
                except exceptions.Iec6205621ParseError:
                    pass
                
            except Exception as err:
                logging.warning(f"Could not decode dataset for line : {err}")

        return TariffResponse(
            data=result,
            bcc=bcc,
            checked=bcc_checked
        )
    