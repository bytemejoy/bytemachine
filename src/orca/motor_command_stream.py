import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class MotorCommandStreamRequest(ModbusRequest):
    function_code = 100
    _rtu_frame_size = 9  # Adjusted for 1 byte sub-function code + 4 byte data

    def __init__(self, sub_function_code, data, **kwargs):
        super().__init__(**kwargs)
        self.sub_function_code = sub_function_code
        self.data = data if isinstance(data, list) else [data]

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        return struct.pack(">Bl", self.sub_function_code, self.data[0])

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        self.sub_function_code, self.data[0] = struct.unpack(">Bl", data)

    def execute(self, context):
        """Execute request."""
        values = context.getValues(self.function_code, 0, 6)
        return MotorCommandStreamResponse(values)


class MotorCommandStreamResponse(ModbusResponse):
    function_code = 100
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
