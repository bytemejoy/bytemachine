import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class ManageHighSpeedStreamRequest(ModbusRequest):
    function_code = 65
    _rtu_frame_size = 12

    def __init__(self, enable, baud_rate, delay_us, **kwargs):
        super().__init__(**kwargs)
        self.enable = enable
        self.baud_rate = baud_rate
        self.delay_us = delay_us

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        sub_function_code = 0xFF00 if self.enable else 0x0000
        return struct.pack(
            ">HHlH", sub_function_code, self.baud_rate, self.delay_us, 0
        )  # Padding with 0

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        self.sub_function_code, self.baud_rate, self.delay_us, _ = struct.unpack(
            ">HHlH", data
        )
        self.enable = self.sub_function_code == 0xFF00

    def execute(self, context):
        """Execute request."""
        values = context.getValues(self.function_code, 0, 3)
        return ManageHighSpeedStreamResponse(values)


class ManageHighSpeedStreamResponse(ModbusResponse):
    function_code = 65
    _rtu_byte_count_pos = 2

    def __init__(self, values=None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.values = values or []
        self.baud_rate = None
        self.delay_us = None

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode response."""
        return struct.pack(">HH", self.baud_rate, self.delay_us)

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode response."""
        self.baud_rate, self.delay_us = struct.unpack(">HH", data)
