"""
Implements the Trinnov Altitude processor automation protocol over TCP/IP
"""

import asyncio
from collections.abc import Callable
import logging
from trinnov_altitude import const, exceptions, messages


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
        self.audiosync: bool | None = None
        self.bypass: bool | None = None
        self.dim: bool | None = None
        self.id: str | None = None
        self.mute: bool | None = None
        self.presets: dict = {}
        self.source: str | None = None
        self.sources: dict = {}
        self.version: str | None = None
        self.volume: float | None = None

        # Utility
        self._callback: Callable[[messages.Message], None] | None = None
        self._reader: asyncio.StreamReader | None = None
        self._response_handler_task: asyncio.Task | None = None
        self._writer: asyncio.StreamWriter | None = None

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

        self._response_handler_task = asyncio.create_task(self._sync())

        await self._send(f"id {self.client_id}", timeout)

    def connected(self):
        return self._reader is not None and self._writer is not None

    async def disconnect(self, timeout=USE_DEFAULT_TIMEOUT):
        """Closes the connection to the processor"""
        if self._writer is None:
            return

        if timeout is self.USE_DEFAULT_TIMEOUT:
            timeout = self.timeout

        if self._response_handler_task:
            self._response_handler_task.cancel()
            try:
                await self._response_handler_task
            except asyncio.CancelledError:
                pass
            self._response_handler_task = None

        await self._send("bye", timeout)
        self._writer.close()
        await asyncio.wait_for(self._writer.wait_closed(), timeout)
        self._reader = None
        self._writer = None

    def register_callback(self, callback: Callable[[messages.Message], None]):
        self._callback = callback

    # --------------------------
    # Commands
    # --------------------------
    async def acoustic_correction_set(
        self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT
    ):
        """
        Set the acoustic correction to On (True) or Off (False)
        """
        await self._send(f"use_acoustic_correct {int(state)}", timeout)

    async def acoustic_correction_toggle(self, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Toggle the acoustic correction state.
        """
        await self._send("use_acoustic_correct 2", timeout)

    async def bypass_set(self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Set the bypass state to On (True) or Off (False)
        """
        await self._send(f"bypass {int(state)}", timeout)

    async def bypass_toggle(self, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Toggle the bypass state.
        """
        await self._send("bypass 2", timeout)

    async def dim_set(self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Set the dim state to On (True) or Off (False)
        """
        await self._send(f"dim {int(state)}", timeout)

    async def dim_toggle(self, timeout=USE_DEFAULT_TIMEOUT):
        """
        Toggle the dim state.
        """
        await self._send("dim 2", timeout)

    async def front_display_set(
        self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT
    ):
        """
        Set the front display of the processor to On (True) or Off (False).
        """
        await self._send(f"fav_light {int(state)}", timeout)

    async def front_display_toggle(self, timeout=USE_DEFAULT_TIMEOUT):
        """
        Toggle the front display of the processor.
        """
        await self._send("dim 2", timeout)

    async def level_alignment_set(
        self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT
    ):
        """
        Set the level alignment state to On (True) or Off (False)
        """
        await self._send(f"use_level_alignment {int(state)}", timeout)

    async def level_alignment_toggle(self, state, timeout=USE_DEFAULT_TIMEOUT):
        """
        Toggle the level alignment state.
        """
        await self._send("use_level_alignment 2", timeout)

    async def mute_set(self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Set the mute state to On (True) or Off (False)
        """
        await self._send(f"mute {int(state)}", timeout)

    async def mute_toggle(self, state, timeout=USE_DEFAULT_TIMEOUT):
        """
        Toggle the mute state.
        """
        await self._send("mute 2", timeout)

    async def page_adjust(self, delta: int, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Changes the menu page currently on the GUI. `delta` indicates the number of
        pages to change, and may be positive or negative.
        """
        await self._send("bypass 2", timeout)

    async def power_off(self, timeout=USE_DEFAULT_TIMEOUT):
        """
        Power off.
        """
        await self._send("power off SECURED FHZMCH48FE", timeout)

    async def preset_load(self, id: int, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Load the preset identified by `id`. Preset `0` is the built-in preset and
        presets >= `1` are user defined presets.
        """
        await self._send("bypass 2", timeout)

    async def quick_optimized_set(
        self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT
    ):
        """
        Set the quick optimized state to On (True) or Off (False)
        """
        await self._send(f"quick_optimized {int(state)}", timeout)

    async def quick_optimized_toggle(self, state, timeout=USE_DEFAULT_TIMEOUT):
        """
        Toggle the quick optimized state.
        """
        await self._send("quick_optimized 2", timeout)

    async def remapping_mode_set(
        self, mode: const.RemappingMode, timeout: float = USE_DEFAULT_TIMEOUT
    ):
        """
        Set the remapping mode. See `const.RemappingMode` for available options
        and descriptions.
        """
        await self._send(f"remapping_mode {mode.value}", timeout)

    async def source_set(self, id: int, timeout: float = USE_DEFAULT_TIMEOUT):
        """
        Set the source identified by `id`, where `0` is the first source.
        """
        await self._send(f"profile {id}", timeout)

    async def time_alignment_set(
        self, state: bool, timeout: float = USE_DEFAULT_TIMEOUT
    ):
        """
        Set the time alignment state to On (True) or Off (False)
        """
        await self._send(f"use_time_alignment {int(state)}", timeout)

    async def time_alignment_toggle(self, state, timeout=USE_DEFAULT_TIMEOUT):
        """
        Toggle the time alignment state.
        """
        await self._send("use_time_alignment 2", timeout)

    async def upmixer_set(
        self, mode: const.UpmixerMode, timeout: float = USE_DEFAULT_TIMEOUT
    ):
        """
        Set the upmixer mode. See `const.UpmixerMode` for available options
        and descriptions.
        """
        await self._send(f"remapping_mode {mode.value}", timeout)

    async def volume_adjust(self, delta: float, timeout=USE_DEFAULT_TIMEOUT):
        """
        Adjust the volume by a relative dB value (float).
        """
        await self._send(f"dvolume {delta}", timeout)

    async def volume_set(self, db: float, timeout=USE_DEFAULT_TIMEOUT):
        """
        Set the volume to an absolute dB value (float).
        """
        await self._send(f"volume {db}", timeout)

    async def volume_ramp(self, db: float, duration: int, timeout=USE_DEFAULT_TIMEOUT):
        """
        Ramp the volume to an absolute dB value (float) over a number of milliseconds (int).
        """
        await self._send(f"volume_ramp {db} {duration}", timeout)

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

    async def _sync(self):  # noqa: C901
        """
        Sync internal state

        Receives all broadcasted messages from the proessor and syncs the
        internal state.
        """
        while True:
            raw_message = await self._receive(None)
            if raw_message is None:
                break

            message = messages.message_factory(raw_message)

            if isinstance(message, messages.AudiosyncMessage):
                self.audiosync = message.state
            elif isinstance(message, messages.BypassMessage):
                self.bypass = message.state
            elif isinstance(message, messages.DimMessage):
                self.dim = message.state
            elif isinstance(message, messages.ErrorMessage):
                self.logger.error(
                    f"Trinnov Altitude responsed with error: {message.error}"
                )
            elif isinstance(message, messages.PresetMessage):
                self.presets[message.index] = message.name
            elif isinstance(message, messages.PresetsClearMessage):
                self.presets = {}
            elif isinstance(message, messages.MuteMessage):
                self.mute = message.state
            elif isinstance(message, messages.SourceMessage):
                self.sources[message.index] = message.name
            elif isinstance(message, messages.SourcesClearMessage):
                self.sources = {}
            elif isinstance(message, messages.SamplingRateMessage):
                self.sampling_rate = message.rate
            elif isinstance(message, messages.VolumeMessage):
                self.volume = message.volume
            elif isinstance(message, messages.WelcomeMessage):
                self.version = message.version
                self.id = message.id

            if self._callback is not None and message is not None:
                self._callback(message)
