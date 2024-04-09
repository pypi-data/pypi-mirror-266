import asyncio
import pytest
import pytest_asyncio

from trinnov_altitude.exceptions import ConnectionFailedError, ConnectionTimeoutError
from trinnov_altitude.trinnov_altitude import TrinnovAltitude
from .mock_trinnov_altitude_server import MockTrinnovAltitudeServer


@pytest_asyncio.fixture
async def mock_server():
    server = MockTrinnovAltitudeServer()
    await server.start_server()
    yield server
    await server.stop_server()


@pytest.mark.asyncio
async def test_connect_failed(mock_server):
    client = TrinnovAltitude(host="invalid")
    with pytest.raises(ConnectionFailedError):
        await client.connect()


@pytest.mark.asyncio
async def test_connect_timeout(mock_server):
    client = TrinnovAltitude(host="1.1.1.1")
    with pytest.raises(ConnectionTimeoutError):
        await client.connect(1)


@pytest.mark.asyncio
async def test_connect(mock_server):
    client = TrinnovAltitude(host="localhost", port=mock_server.port)
    await client.connect()
    assert client.connected() is True
    await client.disconnect()


@pytest.mark.asyncio
async def test_set_volume(mock_server):
    client = TrinnovAltitude(host="localhost", port=mock_server.port)
    await client.connect()
    await client.set_volume(-46)
    await asyncio.sleep(0.1)
    await client.sync()
    assert client.volume == -46.0
    await client.disconnect()


@pytest.mark.asyncio
async def test_adjust_volume(mock_server):
    client = TrinnovAltitude(host="localhost", port=mock_server.port)
    await client.connect()
    await client.adjust_volume(2)
    await asyncio.sleep(0.1)
    await client.sync()
    assert client.volume == -38.0
    await client.disconnect()
