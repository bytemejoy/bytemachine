import struct
from dataclasses import dataclass
from typing import Union

from pymodbus.pdu import ModbusRequest, ModbusResponse

FRAMER_BYTES: int = 4
MANAGE_HIGH_SPEED_STREAM_FUNCTION_CODE: int = 65
MANAGE_HIGH_SPEED_STREAM_RESPONSE_FORMAT: str = ">BIH"
MANAGE_HIGH_SPEED_STREAM_REQUEST_FORMAT: str = ">HIH"
MANAGE_HIGH_SPEED_STREAM_RESPONSE_NUM_EXPECTED_VALUES: int = 3


@dataclass(kw_only=True)
class ManageHighSpeedStreamResult:
    state_command: int
    realized_baud_rate: int
    realized_delay_us: int


class ManageHighSpeedStreamResponse(ModbusResponse):
    function_code: int = MANAGE_HIGH_SPEED_STREAM_FUNCTION_CODE
    _rtu_frame_size: int = (
        struct.calcsize(MANAGE_HIGH_SPEED_STREAM_RESPONSE_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, values: Union[list, None] = None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format: str = MANAGE_HIGH_SPEED_STREAM_RESPONSE_FORMAT
        self.values: list = values or []
        self.result: Union[ManageHighSpeedStreamResult, None] = None
        self._maybe_init_from_values()

    def _maybe_init_from_values(self) -> None:
        """Initialize member variables from supplied values."""
        if self.values:
            self.result = ManageHighSpeedStreamResult(
                state_command=self.values[0],
                realized_baud_rate=self.values[1],
                realized_delay_us=self.values[2],
            )

    def encode(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> Union[bytes, None]:
        """Encode response."""
        if self.values:
            return struct.pack(
                self.format,
                *self.values,
            )

    def decode(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: bytes
    ) -> None:
        """Decode response."""
        self.values = list(
            struct.unpack(
                self.format,
                data[0 : struct.calcsize(self.format)],
            )
        )
        self._maybe_init_from_values()


class ManageHighSpeedStreamRequest(ModbusRequest):
    function_code: int = MANAGE_HIGH_SPEED_STREAM_FUNCTION_CODE
    # +----------------+---------+--------------------------------+---------------------------+
    # | Device Address | 1 byte  | 0x01                           |                           |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Function Code  | 1 byte  | 0x41                           |                           |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Sub-Function   | 2 bytes | enable and apply parameters    | disable and return to     |
    # | Code           |         | 0xFF00                         | default 0x0000            |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Baud rate      | 4 bytes | Target baud rate (bps)         | Ignored                   |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Delay (us)     | 2 bytes | Target Response delay (ms)     | Ignored                   |
    # +----------------+---------+--------------------------------+---------------------------+
    # | CRC            | 2 bytes | CRC-16 (MODBUS) Polynomial 0xA001                          |
    # +----------------+---------+--------------------------------+---------------------------+
    _rtu_frame_size: int = (
        struct.calcsize(MANAGE_HIGH_SPEED_STREAM_REQUEST_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, enable: bool, baud_rate: int, delay_us: int, **kwargs):
        super().__init__(**kwargs)
        self.format: str = MANAGE_HIGH_SPEED_STREAM_REQUEST_FORMAT
        self.enable: bool = enable
        self.baud_rate: int = baud_rate
        self.delay_us: int = delay_us

    def encode(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        sub_function_code: int = 0xFF00 if self.enable else 0x0000
        return struct.pack(
            self.format,
            sub_function_code,
            self.baud_rate,
            self.delay_us,
        )

    def decode(self, data: bytes):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        self.sub_function_code, self.baud_rate, self.delay_us = struct.unpack(
            self.format,
            data,
        )
        self.enable = self.sub_function_code == 0xFF00

    def execute(self, context):
        """Execute request."""
        values: list = context.getValues(
            self.function_code,
            MANAGE_HIGH_SPEED_STREAM_RESPONSE_NUM_EXPECTED_VALUES,
        )
        return ManageHighSpeedStreamResponse(values)
