import struct
from dataclasses import dataclass
from typing import Union

from pymodbus.pdu import ModbusRequest, ModbusResponse

FRAMER_BYTES: int = 4
MOTOR_COMMAND_STREAM_FUNCTION_CODE: int = 100
MOTOR_COMMAND_STREAM_RESPONSE_FORMAT: str = ">IIHBHH"
MOTOR_COMMAND_STREAM_REQUEST_FORMAT: str = ">BI"
MOTOR_COMMAND_STREAM_RESPONSE_NUM_EXPECTED_VALUES: int = 6


@dataclass(kw_only=True)
class MotorCommandStreamResult:
    position_um: int
    force_mN: int
    power_W: int
    temperature_C: int
    voltage_mV: int
    errors: int


class MotorCommandStreamResponse(ModbusResponse):
    function_code: int = MOTOR_COMMAND_STREAM_FUNCTION_CODE
    _rtu_frame_size: int = (
        struct.calcsize(MOTOR_COMMAND_STREAM_RESPONSE_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, values: Union[list, None] = None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format: str = ">IIHBHH"
        self.values: list = values or []
        self.result: Union[MotorCommandStreamResult, None] = None
        self._maybe_init_from_values()

    def _maybe_init_from_values(self) -> None:
        """Initialize result from supplied values."""
        if self.values:
            self.result = MotorCommandStreamResult(
                position_um=self.values[0],
                force_mN=self.values[1],
                power_W=self.values[2],
                temperature_C=self.values[3],
                voltage_mV=self.values[4],
                errors=self.values[5],
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


class MotorCommandStreamRequest(ModbusRequest):
    function_code: int = MOTOR_COMMAND_STREAM_FUNCTION_CODE
    # +----------+--------+--------------------------------------------------+
    # | Field    | Length | Values                                           |
    # +----------+--------+--------------------------------------------------+
    # | Device   | 1 byte | 0x01                                             |
    # | Address  |        |                                                  |
    # +----------+--------+--------------------------------------------------+
    # | Function | 1 byte | 0x64                                             |
    # | Code     |        |                                                  |
    # +----------+--------+--------------------------------------------------+
    # | Sub      | 1 byte | 0x1C       | 0x1E     | 0x20      | 0x22         |
    # | Code     |        | Force      | Position | Kinematic | Haptic Data  |
    # |          |        | Control    | Control  | Data      | Stream       |
    # |          |        | Stream     | Stream   | Stream    | (Available   |
    # |          |        |            |          | (Available| with Orca    |
    # |          |        |            |          | with Orca | firmware     |
    # |          |        |            |          | firmware  | v6.1.7 or    |
    # |          |        |            |          | v6.1.6 or | later)       |
    # |          |        |            |          | later)    |              |
    # +----------+--------+------------+----------+-----------+--------------+
    # | Data     | 4      | Force (mN) | Position | Ignored   | HAPTIC_STATUS|
    # |          | bytes  |            | (µm)     |           | Register     |
    # +----------+--------+------------+----------+-----------+--------------+
    # | CRC      | 2      | CRC-16 (Modbus) Polynomial 0xA001                |
    # |          | bytes  |                                                  |
    # +----------+--------+--------------------------------------------------+
    _rtu_frame_size: int = (
        struct.calcsize(MOTOR_COMMAND_STREAM_REQUEST_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, sub_function_code: int, data: int, **kwargs):
        super().__init__(**kwargs)
        self.format: str = MOTOR_COMMAND_STREAM_REQUEST_FORMAT
        self.sub_function_code: int = sub_function_code
        self.data: int = data

    def encode(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        return struct.pack(
            self.format,
            self.sub_function_code,
            self.data,
        )

    def decode(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: bytes
    ) -> None:
        """Decode request."""
        self.sub_function_code, self.data = struct.unpack(
            self.format,
            data,
        )

    def execute(self, context) -> MotorCommandStreamResponse:
        """Execute request."""
        values = context.getValues(
            self.function_code,
            MOTOR_COMMAND_STREAM_RESPONSE_NUM_EXPECTED_VALUES,
        )
        return MotorCommandStreamResponse(values)
