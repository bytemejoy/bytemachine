import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class MotorCommandStreamRequest(ModbusRequest):
    function_code = 100
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
    _rtu_frame_size = 9  # Adjusted for 1 byte sub-function code + 4 byte data

    def __init__(self, sub_function_code, data, **kwargs):
        super().__init__(**kwargs)
        self.sub_function_code = sub_function_code
        self.data = data if isinstance(data, list) else [data]

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        return struct.pack(">BI", self.sub_function_code, self.data[0])

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        self.sub_function_code, self.data[0] = struct.unpack(">BI", data)

    def execute(self, context):
        """Execute request."""
        values = context.getValues(self.function_code, 6)
        return MotorCommandStreamResponse(values)


class MotorCommandStreamResponse(ModbusResponse):
    function_code = 100
    _rtu_byte_count_pos = 2

    def __init__(self, values=None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format = ">IIHBHH"
        self.values = values or []
        self.position = None
        self.force = None
        self.power = None
        self.temperature = None
        self.voltage = None
        self.errors = None
        self._maybe_init_from_values()

    def _maybe_init_from_values(self):
        """Initialize member variables from supplied values."""
        if self.values:
            self.position = self.values[0]
            self.force = self.values[1]
            self.power = self.values[2]
            self.temperature = self.values[3]
            self.voltage = self.values[4]
            self.errors = self.values[5]

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode response."""
        return struct.pack(
            self.format,
            self.position,
            self.force,
            self.power,
            self.temperature,
            self.voltage,
            self.errors,
        )

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode response."""
        (
            self.position,
            self.force,
            self.power,
            self.temperature,
            self.voltage,
            self.errors,
        ) = struct.unpack(self.format, data[0 : struct.calcsize(self.format)])
        self.values = [
            self.position,
            self.force,
            self.power,
            self.temperature,
            self.voltage,
            self.errors,
        ]
