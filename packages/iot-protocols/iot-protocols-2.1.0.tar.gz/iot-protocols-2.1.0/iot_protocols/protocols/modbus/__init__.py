from .client import ModbusClient
from .exceptions import ModbusConfigurationException


__version__ = "1.0.0"
__author__ = "Delhaye Adrien"


def create_client(configuration: dict) -> ModbusClient:
    if configuration["transport"] == "serial":
        return ModbusClient.with_serial_client(**configuration)
    
    elif configuration["transport"] == "tcp":
        return ModbusClient.with_tcp_client(**configuration)
    
    else:
        raise ModbusConfigurationException(f"Invalid configuration for Modbus protocol.")