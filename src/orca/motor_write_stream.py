import struct
from dataclasses import dataclass
from typing import Union

from pymodbus.pdu import ModbusRequest, ModbusResponse

FRAMER_BYTES: int = 4
MOTOR_WRITE_STREAM_FUNCTION_CODE: int = 105
MOTOR_WRITE_STREAM_RESPONSE_FORMAT: str = ">BiiHBHH"
MOTOR_WRITE_STREAM_REQUEST_FORMAT: str = ">HBI"
MOTOR_WRITE_STREAM_RESPONSE_NUM_EXPECTED_VALUES: int = 7


@dataclass(kw_only=True)
class MotorWriteStreamResult:
    mode: int
    position_um: int
    force_mN: int
    power_W: int
    temperature_C: int
    voltage_mV: int
    errors: int


class MotorWriteStreamResponse(ModbusResponse):
    function_code: int = MOTOR_WRITE_STREAM_FUNCTION_CODE
    _rtu_frame_size: int = (
        struct.calcsize(MOTOR_WRITE_STREAM_RESPONSE_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, values: Union[list, None] = None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format: str = MOTOR_WRITE_STREAM_RESPONSE_FORMAT
        self.values: list = values or []
        self.result: Union[MotorWriteStreamResult, None] = None
        self._maybe_init_from_values()

    def _maybe_init_from_values(self):
        """Initialize member variables from supplied values."""
        if self.values:
            self.result = MotorWriteStreamResult(
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


class MotorWriteStreamRequest(ModbusRequest):
    function_code: int = MOTOR_WRITE_STREAM_FUNCTION_CODE
    # +------------------+---------+--------------------------------------------------------+
    # | Device Address   | 1 byte  | 0x01                                                   |
    # +------------------+---------+--------------------------------------------------------+
    # | Function Code    | 1 byte  | 0x69                                                   |
    # +------------------+---------+--------------------------------------------------------+
    # | Register Address | 2 bytes | The address of the register in the motor's memory map  |
    # |                  |         | to write to                                            |
    # +------------------+---------+--------------------------------------------------------+
    # | Register Width   | 1 byte  | Specifies 1 if single wide register (16 bits of data)  |
    # |                  |         | or use 2 if register is double wide (32 bits of data)  |
    # +------------------+---------+--------------------------------------------------------+
    # | Register Data    | 4 bytes | If width is specified as 1 the first 2 bytes will be   |
    # |                  |         | ignored.                                               |
    # +------------------+---------+--------------------------------------------------------+
    # | CRC              | 2 bytes | CRC-16 (Modbus) Polynomial 0xA001                      |
    # +------------------+---------+--------------------------------------------------------+
    _rtu_frame_size: int = (
        struct.calcsize(MOTOR_WRITE_STREAM_REQUEST_FORMAT) + FRAMER_BYTES
    )

    def __init__(self, register_address: int, register_width: int, data: int, **kwargs):
        super().__init__(**kwargs)
        self.format: str = MOTOR_WRITE_STREAM_REQUEST_FORMAT
        self.register_address: int = register_address
        self.register_width: int = register_width
        self.data: int = data

    def encode(self) -> bytes:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        return struct.pack(
            self.format,
            self.register_address,
            self.register_width,
            self.data,
        )

    def decode(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: bytes
    ) -> None:
        """Decode request."""
        self.register_address, self.register_width, self.data = struct.unpack(
            self.format,
            data,
        )

    def execute(self, context) -> MotorWriteStreamResponse:
        """Execute request."""
        values: list = context.getValues(
            self.function_code,
            MOTOR_WRITE_STREAM_RESPONSE_NUM_EXPECTED_VALUES,
        )
        return MotorWriteStreamResponse(values)
