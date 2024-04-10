import logging
import pytest
from iot_protocols.protocols.iec62056.client import SerialClient, TariffResponse, messages
from iot_protocols.devices.iec62056_meter import IEC62056SerialMeter


@pytest.fixture
def client() -> SerialClient:
    return SerialClient(
        baudrate=9600,
        port="COM3",
        transport="serial",
        parity="E",
        bytesize=7,
        stopbits=1
    )


def test_client_identification(client: SerialClient):
    result = client.read_tariff_identification("5987893", ack_stop=True)
    logging.info(result)
    assert isinstance(result, messages.IdentificationMessage)

    logging.info(f"----- Next Step ----")

    result = client.request(meter_address="5987893", table=0, timeout=3)
    assert isinstance(result, TariffResponse)
    for dataset in result.data:
        logging.info(f"{dataset}")

@pytest.fixture
def meter() -> IEC62056SerialMeter:
    return IEC62056SerialMeter(
        meter_id="5987893",
        port="COM3"
    )


def test_read_meter_identification(meter: IEC62056SerialMeter):
    meter.connect()
    assert meter.device_id is not None
    assert meter.hardware is not None
    logging.info(f"Meter id : {meter.device_id}")