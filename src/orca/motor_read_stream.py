import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class MotorReadStreamRequest(ModbusRequest):
    function_code = 104
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
    _rtu_frame_size = 7

    def __init__(self, register_address, register_width, **kwargs):
        super().__init__(**kwargs)
        self.register_address = register_address
        self.register_width = register_width

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        return struct.pack(">HB", self.register_address, self.register_width)

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        self.register_address, self.register_width = struct.unpack(">HB", data)

    def execute(self, context):
        """Execute request."""
        values = context.getValues(self.function_code, 8)
        return MotorReadStreamResponse(values)


class MotorReadStreamResponse(ModbusResponse):
    function_code = 104
    _rtu_frame_size = 24

    def __init__(self, values=None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format = ">IBIIHBHH"
        self.values = values or []
        self.register_value = None
        self.mode = None
        self.position = None
        self.force = None
        self.power = None
        self.temperature = None
        self.voltage = None
        self.errors = None
        self._maybe_init_from_values()

    def _maybe_init_from_values(self):
        """Initialize member variables from values."""
        if self.values:
            self.register_value = self.values[0]
            self.mode = self.values[1]
            self.position = self.values[2]
            self.force = self.values[3]
            self.power = self.values[4]
            self.temperature = self.values[5]
            self.voltage = self.values[6]
            self.errors = self.values[7]

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode response."""
        return struct.pack(
            self.format,
            self.register_value,
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
            self.register_value,
            self.mode,
            self.position,
            self.force,
            self.power,
            self.temperature,
            self.voltage,
            self.errors,
        ) = struct.unpack(self.format, data[0 : struct.calcsize(self.format)])
        self.values = [
            self.register_value,
            self.mode,
            self.position,
            self.force,
            self.power,
            self.temperature,
            self.voltage,
            self.errors,
        ]
