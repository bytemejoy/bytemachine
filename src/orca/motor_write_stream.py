import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class MotorWriteStreamRequest(ModbusRequest):
    function_code = 105
    _rtu_frame_size = 10  # 2 byte address + 1 byte width + 4 byte data

    def __init__(self, register_address, register_width, data, **kwargs):
        super().__init__(**kwargs)
        self.register_address = register_address
        self.register_width = register_width
        self.data = data

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        if self.register_width == 1:
            return struct.pack(
                ">HBH", self.register_address, self.register_width, self.data
            )
        else:
            return struct.pack(
                ">HBl", self.register_address, self.register_width, self.data
            )

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        if self.register_width == 1:
            self.register_address, self.register_width, self.data = struct.unpack(
                ">HBH", data
            )
        else:
            self.register_address, self.register_width, self.data = struct.unpack(
                ">HBl", data
            )

    def execute(self, context):
        """Execute request."""
        values = context.getValues(self.function_code, 0, 6)
        return MotorWriteStreamResponse(values)


class MotorWriteStreamResponse(ModbusResponse):
    function_code = 105
    _rtu_byte_count_pos = 2

    def __init__(self, values=None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.values = values or []
        self.position = None
        self.force = None
        self.power = None
        self.temperature = None
        self.voltage = None
        self.errors = None

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode response."""
        return struct.pack(
            ">llhBHH",
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
        ) = struct.unpack(">llhBHH", data)
