import struct
from dataclasses import dataclass
from typing import Union

from pymodbus.pdu import ModbusRequest, ModbusResponse

FRAMER_BYTES: int = 4
MOTOR_READ_STREAM_FUNCTION_CODE: int = 104
MOTOR_READ_STREAM_RESPONSE_FORMAT: str = ">IBIIHBHH"
MOTOR_READ_STREAM_REQUEST_FORMAT: str = ">HB"
MOTOR_READ_STREAM_RESPONSE_NUM_EXPECTED_VALUES: int = 8


@dataclass(kw_only=True)
class MotorReadStreamResult:
    register_value: int
    mode: int
    position_um: int
    force_mN: int
    power_W: int
    temperature_C: int
    voltage_mV: int
    errors: int


class MotorReadStreamResponse(ModbusResponse):
    function_code: int = MOTOR_READ_STREAM_FUNCTION_CODE
    _rtu_frame_size: int = (
        struct.calcsize(MOTOR_READ_STREAM_RESPONSE_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, values: Union[list, None] = None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format: str = MOTOR_READ_STREAM_RESPONSE_FORMAT
        self.values: list = values or []
        self.result: Union[MotorReadStreamResult, None] = None
        self._maybe_init_from_values()

    def _maybe_init_from_values(self):
        """Initialize member variables from values."""
        if self.values:
            self.result = MotorReadStreamResult(
                register_value=self.values[0],
                mode=self.values[1],
                position_um=self.values[2],
                force_mN=self.values[3],
                power_W=self.values[4],
                temperature_C=self.values[5],
                voltage_mV=self.values[6],
                errors=self.values[7],
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


class MotorReadStreamRequest(ModbusRequest):
    function_code: int = MOTOR_READ_STREAM_FUNCTION_CODE
    # +------------------+----------+------------------------------------------------+
    # | Device Address   | 1 byte   | 0x01                                           |
    # +------------------+----------+------------------------------------------------+
    # | Function Code    | 1 byte   | 0x68                                           |
    # +------------------+----------+------------------------------------------------+
    # | Register Address | 2 bytes  | The address of the register in the motor's     |
    # |                  |          | memory map to read from                        |
    # +------------------+----------+------------------------------------------------+
    # | Register Width   | 1 byte   | Specifies 1 if single wide register (16 bits   |
    # |                  |          | of data) or use 2 if register is double wide   |
    # |                  |          | (32 bits of data)                              |
    # +------------------+----------+------------------------------------------------+
    # | CRC              | 2 bytes  | CRC-16 (Modbus) Polynomial 0xA001              |
    # +------------------+----------+------------------------------------------------+
    _rtu_frame_size: int = (
        struct.calcsize(MOTOR_READ_STREAM_REQUEST_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, register_address: int, register_width: int, **kwargs):
        super().__init__(**kwargs)
        self.format: str = MOTOR_READ_STREAM_REQUEST_FORMAT
        self.register_address: int = register_address
        self.register_width: int = register_width

    def encode(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        return struct.pack(
            self.format,
            self.register_address,
            self.register_width,
        )

    def decode(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: bytes
    ) -> None:
        """Decode request."""
        self.register_address, self.register_width = struct.unpack(
            self.format,
            data,
        )

    def execute(self, context) -> MotorReadStreamResponse:
        """Execute request."""
        values: list = context.getValues(
            self.function_code,
            MOTOR_READ_STREAM_RESPONSE_NUM_EXPECTED_VALUES,
        )
        return MotorReadStreamResponse(values)
