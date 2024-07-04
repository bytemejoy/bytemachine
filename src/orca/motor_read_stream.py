import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class MotorReadStreamRequest(ModbusRequest):
    function_code = 104
    _rtu_frame_size = 6

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
        # Add any validation if needed
        # ...
        values = context.getValues(
            self.function_code, 0, 8
        )  # Assuming 8 values in response
        return MotorReadStreamResponse(values, register_width=self.register_width)


class MotorReadStreamResponse(ModbusResponse):
    function_code = 104
    _rtu_byte_count_pos = 2

    def __init__(self, values=None, register_width=1, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.register_width = register_width  # Store register width for encoding
        self.values = values or []
        self.register_value = None
        self.position = None
        self.force = None
        self.power = None
        self.temperature = None
        self.voltage = None
        self.errors = None

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode response."""
        if self.register_width == 1:
            return struct.pack(
                ">HllhBHH",
                self.register_value,
                self.position,
                self.force,
                self.power,
                self.temperature,
                self.voltage,
                self.errors,
            )
        else:
            return struct.pack(
                ">llhBHH",
                self.register_value,
                self.position,
                self.force,
                self.power,
                self.temperature,
                self.voltage,
                self.errors,
            )

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode response."""
        if self.register_width == 1:
            (
                self.register_value,
                self.position,
                self.force,
                self.power,
                self.temperature,
                self.voltage,
                self.errors,
            ) = struct.unpack(">HllhBHH", data)
        else:
            (
                self.register_value,
                self.position,
                self.force,
                self.power,
                self.temperature,
                self.voltage,
                self.errors,
            ) = struct.unpack(">llhBHH", data)
