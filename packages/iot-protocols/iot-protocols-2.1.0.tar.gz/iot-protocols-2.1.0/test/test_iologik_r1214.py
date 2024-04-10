
import logging
import pytest

from iot_protocols.devices.moxa_iologik_r1214 import MoxaIoLogikR1214, RelayState, IOState


class TestMoxaIoLogikR1214:
    
    __device: MoxaIoLogikR1214 = None

    @pytest.fixture
    def device(self) -> MoxaIoLogikR1214:
        if self.__device is None:    
            self.__device = MoxaIoLogikR1214(
                modbus_id=1,
                port="COM3"
            )
        return self.__device
    
    def test_read_device_profile(self, device: MoxaIoLogikR1214) -> None:
        device.connect()
        assert device.profile is not None
        logging.info(device.profile)
        assert device.device_id is not None
        logging.info(device.hardware)
        


    def test_set_and_read_relay(self, device: MoxaIoLogikR1214) -> None:
        if not device.is_connected:
            device.connect()

        for i in range(6):    
            device.set_relay(
                "OPEN",
                i
            )
            result = device.read_relay(i)
            logging.info(f"Relay {i} --> {result!r}")
            assert isinstance(result, RelayState)
            assert result.name == "OPEN"

        for i in range(6):    
            device.set_relay(
                "CLOSED",
                i
            )
            result = device.read_relay(i)
            logging.info(f"Relay {i} --> {result!r}")
            assert isinstance(result, RelayState)
            assert result.name == "CLOSED"


    def test_read_io(self, device: MoxaIoLogikR1214):
        result = device.read_io_array() 
        logging.info(f"IO --> {result}")
        for io in result:
            assert isinstance(io, IOState)

    def test_switch_all_relay(self, device: MoxaIoLogikR1214):
        device.set_relay_array(
            [RelayState(0) for i in range(6)]
        )

        result = device.read_relay_array()
        for res in result:
            assert isinstance(res, RelayState)
            assert res == RelayState(0)

