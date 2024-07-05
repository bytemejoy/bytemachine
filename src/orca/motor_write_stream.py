import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class MotorWriteStreamRequest(ModbusRequest):
    function_code = 105
    # - [Device Address] 1 byte: 0x01
    # - [Function Code] 1 byte: 0x69
    # - [Register Address] 2 bytes: The address of the register in the motor’s memory map
    #   to write to
    # - [Register Width] 1 byte: Specifies 1 if single wide register (16 bits of data) or use
    #    2 if register is double wide (32 bits of data)
    # - [Register Data] 4 bytes: If width is specified as 1 the first 2 bytes will be ignored.
    # - [CRC] 2 bytes: CRC-16 (Modbus) Polynomial 0xA001
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
    _rtu_frame_size = 11

    def __init__(self, register_address, register_width, data, **kwargs):
        super().__init__(**kwargs)
        self.register_address = register_address
        self.register_width = register_width
        self.data = data

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        if self.register_width == 1:
            return struct.pack(
                ">HBHH", self.register_address, self.register_width, 0, self.data
            )
        else:
            return struct.pack(
                ">HBI", self.register_address, self.register_width, self.data
            )

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        if self.register_width == 1:
            self.register_address, self.register_width, _, self.data = struct.unpack(
                ">HBHH", data
            )
        else:
            self.register_address, self.register_width, self.data = struct.unpack(
                ">HBI", data
            )

    def execute(self, context):
        """Execute request."""
        values = context.getValues(self.function_code, 7)
        return MotorWriteStreamResponse(values)


class MotorWriteStreamResponse(ModbusResponse):
    function_code = 105
    _rtu_frame_size = 20

    def __init__(self, values=None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format = ">BIIHBHH"
        self.values = values or []
        self.mode = None
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
            self.mode = self.values[0]
            self.position = self.values[1]
            self.force = self.values[2]
            self.power = self.values[3]
            self.temperature = self.values[4]
            self.voltage = self.values[5]
            self.errors = self.values[6]

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode response."""
        return struct.pack(
            self.format,
            self.mode,
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
            self.mode,
            self.position,
            self.force,
            self.power,
            self.temperature,
            self.voltage,
            self.errors,
        ) = struct.unpack(self.format, data[0 : struct.calcsize(self.format)])
        self.values = [
            self.mode,
            self.position,
            self.force,
            self.power,
            self.temperature,
            self.voltage,
            self.errors,
        ]
