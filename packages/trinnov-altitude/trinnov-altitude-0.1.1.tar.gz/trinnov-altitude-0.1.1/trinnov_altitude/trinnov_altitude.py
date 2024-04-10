"""
Implements the Trinnov Altitude processor automation protocol over TCP/IP
"""

import asyncio
import logging
import re
from trinnov_altitude import exceptions


class TrinnovAltitude:
    """
    Trinnov Altitude

    A class for interfacing with the Trinnov Altitude processor via the TCP/IP protocol.
    """

    DEFAULT_CLIENT_ID = "py-trinnov-altitude"
    DEFAULT_PORT = 44100
    DEFAULT_TIMEOUT = 2.0
    ENCODING = "ascii"

    # Use a sentinel value to signal that the DEFAULT_TIMEOUT should be used.
    # This allows users to pass None and disable the timeout to wait indefinitely.
    USE_DEFAULT_TIMEOUT = -1.0

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        client_id: str = DEFAULT_CLIENT_ID,
        timeout: float = DEFAULT_TIMEOUT,
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        # Settings
        self.host = host
        self.port = port
        self.client_id = client_id
        self.timeout = timeout
        self.logger = logger

        # State
        self.dim = None
        self.id = None
        self.mute = None
        self.version = None
        self.volume = None

        # Utility
        self._reader = None
        self._writer = None

    # --------------------------
    # Connection
    # --------------------------

    async def connect(self, timeout=USE_DEFAULT_TIMEOUT):
        """Initiates connection to the processor"""
        self.logger.info("Connecting to Altitude: %s:%s", self.host, self.port)

        if timeout is self.USE_DEFAULT_TIMEOUT:
            timeout = self.timeout

        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), timeout
            )
        except asyncio.TimeoutError:
            raise exceptions.ConnectionTimeoutError
        except Exception as e:
            raise exceptions.ConnectionFailedError(e)

        await self._send(f"id {self.client_id}", timeout)

    def connected(self):
        return self._reader is not None and self._writer is not None

    async def sync(self, timeout=USE_DEFAULT_TIMEOUT):
        """
        Sync internal state

        Receives all broadcasted messages from the proessor and syncs the
        internal state.
        """
        while True:
            message = await self._receive(timeout)
            if message is None:
                break

            if match := re.match(r"^DIM\s(-?\d+)", message):
                self.dim = bool(int(match.group(1)))
            elif match := re.match(r"^ERROR: (.*)", message):
                error = match.group(1)
                self.logger.error(f"Trinnov Altitude responses with error: {error}")
            elif match := re.match(r"^MUTE\s(0|1)", message):
                self.mute = bool(int(match.group(1)))
            elif match := re.match(r"^VOLUME\s(-?\d+(\.\d+)?)", message):
                self.volume = float(match.group(1))
            elif match := re.match(
                r"^Welcome on Trinnov Optimizer \(Version (\S+), ID (\d+)\)",
                message,
            ):
                self.version = match.group(1)
                self.id = match.group(2)

    async def disconnect(self, timeout=USE_DEFAULT_TIMEOUT):
        """Closes the connection to the processor"""
        if self._writer is None:
            return

        if timeout is self.USE_DEFAULT_TIMEOUT:
            timeout = self.timeout

        self._writer.close()
        await asyncio.wait_for(self._writer.wait_closed(), timeout)
        self._reader = None
        self._writer = None

    # --------------------------
    # Commands
    # --------------------------

    async def set_volume(self, db: int, timeout=USE_DEFAULT_TIMEOUT):
        """
        Set the master volume to an absolute value.
        """
        await self._send(f"volume {db}", timeout)

    async def adjust_volume(self, delta: int, timeout=USE_DEFAULT_TIMEOUT):
        """
        Adjust the master value by a relative value.
        """
        await self._send(f"dvolume {delta}", timeout)

    async def ramp_volume(self, db: int, duration: int, timeout=USE_DEFAULT_TIMEOUT):
        """
        Ramp the master volume to an absolute value over a number of milliseconds.
        """
        await self._send(f"volume_ramp {db} {duration}", timeout)

    async def power_off(self, timeout=USE_DEFAULT_TIMEOUT):
        """
        Power off.
        """
        await self._send("power off SECURED FHZMCH48FE", timeout)

    # --------------------------
    # Utility
    # --------------------------

    async def _receive(self, timeout):
        """Receives a single message from the processor"""
        if self._reader is None:
            raise exceptions.NotConnectedError()

        if timeout is self.USE_DEFAULT_TIMEOUT:
            timeout = self.timeout

        try:
            message = await asyncio.wait_for(self._reader.readline(), timeout)
            message = message.decode().rstrip()

            if message == "":
                await self.disconnect(timeout)
                return None

            self.logger.debug(f"Received from Altitude: {message}")
            return message
        except asyncio.TimeoutError:
            return None

    async def _send(self, message: str, timeout):
        """Sends a message to the processor"""
        if self._writer is None:
            raise exceptions.NotConnectedError()

        if timeout is self.USE_DEFAULT_TIMEOUT:
            timeout = self.timeout

        if not message.endswith("\n"):
            message += "\n"

        message_bytes = message.encode(self.ENCODING)
        self._writer.write(message_bytes)
        await asyncio.wait_for(self._writer.drain(), timeout=timeout)
        self.logger.debug(f"Sent to Altitude: {message.rstrip()}")
