from typing import Union

from pymodbus.client.serial import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.framer import Framer
from pymodbus.pdu import ModbusResponse

from src.orca.manage_high_speed_stream import (
    ManageHighSpeedStreamRequest,
    ManageHighSpeedStreamResponse,
    ManageHighSpeedStreamResult,
)
from src.orca.motor_command_stream import (
    MotorCommandStreamRequest,
    MotorCommandStreamResponse,
    MotorCommandStreamResult,
)
from src.orca.motor_read_stream import (
    MotorReadStreamRequest,
    MotorReadStreamResponse,
    MotorReadStreamResult,
)
from src.orca.motor_write_stream import (
    MotorWriteStreamRequest,
    MotorWriteStreamResponse,
    MotorWriteStreamResult,
)


class OrcaActuator:
    """
    Class representing an Orca Series Modbus RTU actuator.
    """

    def __init__(self, port: str, timeout: int = 1):
        """
        Initializes the OrcaActuator object.

        Args:
            port (str): The serial port the actuator is connected to.
            timeout (int): The timeout for Modbus requests in seconds (default: 1).
        """
        self.framer: Framer = Framer.RTU
        self.port: str = port
        self.slave_address: int = 1
        self.baudrate: int = 19200
        self.timeout: int = timeout
        self.stop_bits: int = 1
        self.parity: str = "E"
        self.client: AsyncModbusSerialClient = AsyncModbusSerialClient(
            framer=self.framer,
            port=self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stop_bits,
            timeout=self.timeout,
        )
        self.client.silent_interval = 0.002
        self.client.register(
            ManageHighSpeedStreamResponse  # pyright: ignore[reportArgumentType]
        )
        self.client.register(
            MotorCommandStreamResponse  # pyright: ignore[reportArgumentType]
        )
        self.client.register(
            MotorReadStreamResponse  # pyright: ignore[reportArgumentType]
        )
        self.client.register(
            MotorWriteStreamResponse  # pyright: ignore[reportArgumentType]
        )

    async def connect(self) -> bool:
        """
        Starts the Modbus connection to the actuator.

        Returns:
            bool: True if connection was successful else False.
        """
        connection_successful: bool = await self.client.connect()
        return connection_successful

    async def read_register(self, address: int, count: int = 1) -> Union[list, None]:
        """
        Reads one or more registers from the actuator.

        Args:
            address (int): The starting address of the register(s) to read.
            count (int): The number of registers to read (default: 1).

        Returns:
            list: A list of register values, or None if the read failed.
        """
        try:
            response: ModbusResponse = await self.client.read_holding_registers(
                address, count, slave=self.slave_address
            )
            if response.isError():
                print(f"Error reading register(s): {response}")
                return None
            return response.registers
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return None

    async def write_register(self, address: int, value: int) -> bool:
        """
        Writes a value to a single register in the actuator.

        Args:
            address (int): The address of the register to write to.
            value (int): The value to write to the register.

        Returns:
            bool: True if the write was successful, False otherwise.
        """
        try:
            response: ModbusResponse = await self.client.write_register(
                address, value, slave=self.slave_address
            )
            if response.isError():
                print(f"Error writing register: {response}")
                return False
            return True
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return False

    async def write_registers(self, address: int, values: list) -> bool:
        """
        Writes multiple values to consecutive registers in the actuator.

        Args:
            address (int): The starting address of the registers to write to.
            values (list): A list of values to write to the registers.

        Returns:
            bool: True if the write was successful, False otherwise.
        """
        try:
            response: ModbusResponse = await self.client.write_registers(
                address, values, slave=self.slave_address
            )
            if response.isError():
                print(f"Error writing registers: {response}")
                return False
            return True
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return False

    async def manage_high_speed_stream(
        self, enable: bool, baud_rate: int, delay_us: int
    ) -> Union[ManageHighSpeedStreamResult, None]:
        """
        Manages the high-speed stream parameters of the actuator.
        """
        request = ManageHighSpeedStreamRequest(enable, baud_rate, delay_us)
        response: ManageHighSpeedStreamResponse = await self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error managing high-speed stream: {response}")
            return None
        return response.result

    async def motor_command_stream(
        self, sub_function_code: int, data: int
    ) -> Union[MotorCommandStreamResult, None]:
        """
        Sends a motor command stream message to the actuator.
        """
        request = MotorCommandStreamRequest(
            sub_function_code, data, slave=self.slave_address
        )
        response: MotorCommandStreamResponse = await self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error sending motor command stream: {response}")
            return None
        response.result

    async def motor_read_stream(
        self, register_address: int, register_width: int
    ) -> Union[MotorReadStreamResult, None]:
        """
        Reads a register value from the actuator using the motor read stream function.
        """
        request = MotorReadStreamRequest(
            register_address, register_width, slave=self.slave_address
        )
        response: MotorReadStreamResponse = await self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error sending motor read stream: {response}")
            return None
        return response.result

    async def motor_write_stream(
        self, register_address: int, register_width: int, data: int
    ) -> Union[MotorWriteStreamResult, None]:
        """
        Writes a value to a register in the actuator using the motor write stream function.
        """
        request = MotorWriteStreamRequest(
            register_address, register_width, data, slave=self.slave_address
        )
        response: MotorWriteStreamResponse = await self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error sending motor write stream: {response}")
            return None
        response.result

    async def auto_zero(self, max_force: int, exit_to_mode: int) -> bool:
        """
        Auto zeros the actuator using up to max_force and exiting to mode exit_to_mode when complete.
        """
        write_successful: bool = await self.write_registers(
            171, [2, max_force, exit_to_mode]
        )
        return await self.write_register(3, 55) | write_successful

    async def set_mode(self, mode: int) -> bool:
        """Set actuator mode."""
        return await self.write_register(3, mode)

    async def configure_kinematic_motion(
        self,
        motion_id: int,
        position_target: int,
        settling_time: int,
        auto_start_delay: int,
        next_id: int,
        motion_type: int,
        auto_start_next: int,
    ) -> bool:
        """
        Configures/sets a kinematic motion.
        """
        position_target_low: int = position_target & 0xFF
        position_target_high: int = position_target >> 8 & 0xFF
        settling_time_low: int = settling_time & 0xFF
        settling_time_high: int = settling_time >> 8 & 0xFF
        next_type_auto: int = next_id << 3 + motion_type << 1 + auto_start_next
        return await self.write_registers(
            780 + 6 * motion_id,
            [
                position_target_low,
                position_target_high,
                settling_time_low,
                settling_time_high,
                auto_start_delay,
                next_type_auto,
            ],
        )

    def close(self) -> None:
        """
        Closes the Modbus connection.
        """
        self.client.close()
