import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse


class ManageHighSpeedStreamRequest(ModbusRequest):
    function_code = 65
    # +----------------+---------+--------------------------------+---------------------------+
    # | Device Address | 1 byte  | 0x01                           |                           |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Function Code  | 1 byte  | 0x41                           |                           |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Sub-Function   | 2 bytes | enable and apply parameters    | disable and return to     |
    # | Code           |         | 0xFF00                         | default 0x0000            |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Baud rate      | 4 bytes | Target baud rate (bps)         | Ignored                   |
    # +----------------+---------+--------------------------------+---------------------------+
    # | Delay (us)     | 2 bytes | Target Response delay (ms)     | Ignored                   |
    # +----------------+---------+--------------------------------+---------------------------+
    # | CRC            | 2 bytes | CRC-16 (MODBUS) Polynomial 0xA001                          |
    # +----------------+---------+--------------------------------+---------------------------+
    _rtu_frame_size = 12

    def __init__(self, enable, baud_rate, delay_us, **kwargs):
        super().__init__(**kwargs)
        self.enable = enable
        self.baud_rate = baud_rate
        self.delay_us = delay_us

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode request."""
        sub_function_code = 0xFF00 if self.enable else 0x0000
        return struct.pack(">HIH", sub_function_code, self.baud_rate, self.delay_us)

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode request."""
        self.sub_function_code, self.baud_rate, self.delay_us = struct.unpack(
            ">HIH", data
        )
        self.enable = self.sub_function_code == 0xFF00

    def execute(self, context):
        """Execute request."""
        values = context.getValues(self.function_code, 3)
        return ManageHighSpeedStreamResponse(values)


class ManageHighSpeedStreamResponse(ModbusResponse):
    function_code = 65
    _rtu_frame_size = 11

    def __init__(self, values=None, **kwargs):
        """Initialize response."""
        ModbusResponse.__init__(self, **kwargs)
        self.format = ">BIH"
        self.values = values or []
        self.state_command = None
        self.baud_rate = None
        self.delay_us = None
        self._maybe_init_from_values()

    def _maybe_init_from_values(self):
        """Initialize member variables from supplied values."""
        if self.values:
            self.state_command = self.values[0]
            self.baud_rate = self.values[1]
            self.delay_us = self.values[2]

    def encode(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Encode response."""
        return struct.pack(
            self.format, self.state_command, self.baud_rate, self.delay_us
        )

    def decode(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        """Decode response."""
        (
            self.state_command,
            self.baud_rate,
            self.delay_us,
        ) = struct.unpack(self.format, data[0 : struct.calcsize(self.format)])
        self.values = [
            self.state_command,
            self.baud_rate,
            self.delay_us,
        ]
