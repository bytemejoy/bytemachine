from pymodbus.client.serial import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.framer import Framer

from src.orca.manage_high_speed_stream import (
    ManageHighSpeedStreamRequest,
    ManageHighSpeedStreamResponse,
)
from src.orca.motor_command_stream import (
    MotorCommandStreamRequest,
    MotorCommandStreamResponse,
)
from src.orca.motor_read_stream import MotorReadStreamRequest, MotorReadStreamResponse
from src.orca.motor_write_stream import (
    MotorWriteStreamRequest,
    MotorWriteStreamResponse,
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
        self.framer = Framer.RTU
        self.port = port
        self.slave_address = 1
        self.baudrate = 19200
        self.timeout = timeout
        self.stop_bits = 1
        self.parity = "E"
        self.client = ModbusClient(
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
        self.client.connect()
        self.sleep()

    def read_register(self, address: int, count: int = 1):
        """
        Reads one or more registers from the actuator.

        Args:
            address (int): The starting address of the register(s) to read.
            count (int): The number of registers to read (default: 1).

        Returns:
            list: A list of register values, or None if the read failed.
        """
        try:
            response = self.client.read_holding_registers(
                address, count, slave=self.slave_address
            )
            if response.isError():
                print(f"Error reading register(s): {response}")
                return None
            return response.registers
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return None

    def write_register(self, address: int, value: int):
        """
        Writes a value to a single register in the actuator.

        Args:
            address (int): The address of the register to write to.
            value (int): The value to write to the register.

        Returns:
            bool: True if the write was successful, False otherwise.
        """
        try:
            response = self.client.write_register(
                address, value, slave=self.slave_address
            )
            if response.isError():
                print(f"Error writing register: {response}")
                return False
            return True
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return False

    def write_registers(self, address: int, values: list):
        """
        Writes multiple values to consecutive registers in the actuator.

        Args:
            address (int): The starting address of the registers to write to.
            values (list): A list of values to write to the registers.

        Returns:
            bool: True if the write was successful, False otherwise.
        """
        try:
            response = self.client.write_registers(
                address, values, slave=self.slave_address
            )
            if response.isError():
                print(f"Error writing registers: {response}")
                return False
            return True
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return False

    def manage_high_speed_stream(self, enable, baud_rate, delay_us):
        """
        Manages the high-speed stream parameters of the actuator.
        """
        request = ManageHighSpeedStreamRequest(enable, baud_rate, delay_us)
        response: ManageHighSpeedStreamResponse = self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error managing high-speed stream: {response}")
            return None
        return (
            response.state_command,
            response.baud_rate,
            response.delay_us,
        )

    def motor_command_stream(self, sub_function_code, data):
        """
        Sends a motor command stream message to the actuator.
        """
        request = MotorCommandStreamRequest(
            sub_function_code, data, slave=self.slave_address
        )
        response: MotorCommandStreamResponse = self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error sending motor command stream: {response}")
            return None
        return (
            response.position,
            response.force,
            response.power,
            response.temperature,
            response.voltage,
            response.errors,
        )

    def motor_read_stream(self, register_address, register_width):
        """
        Reads a register value from the actuator using the motor read stream function.
        """
        request = MotorReadStreamRequest(
            register_address, register_width, slave=self.slave_address
        )
        response: MotorReadStreamResponse = self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error sending motor read stream: {response}")
            return None
        return (
            response.register_value,
            response.mode,
            response.position,
            response.force,
            response.power,
            response.temperature,
            response.voltage,
            response.errors,
        )

    def motor_write_stream(self, register_address, register_width, data):
        """
        Writes a value to a register in the actuator using the motor write stream function.
        """
        request = MotorWriteStreamRequest(
            register_address, register_width, data, slave=self.slave_address
        )
        response: MotorWriteStreamResponse = self.client.execute(
            request
        )  # pyright: ignore[reportAssignmentType]
        if response.isError():
            print(f"Error sending motor write stream: {response}")
            return None
        return (
            response.mode,
            response.position,
            response.force,
            response.power,
            response.temperature,
            response.voltage,
            response.errors,
        )

    def auto_zero(self, max_force, exit_to_mode):
        """
        Auto zeros the actuator using up to max_force and exiting to mode exit_to_mode when complete.
        """
        self.write_registers(171, [2, max_force, exit_to_mode])
        self.write_register(3, 55)
        print("Performing auto zero")
        while True:
            mode = self.read_register(317)
            if mode is not None and mode[0] == 1:
                break
        print("Auto zero complete")

    def sleep(self):
        """Puts the actuator into sleep mode."""
        self.write_register(3, 1)

    def configure_kinematic_motion(
        self,
        motion_id,
        position_target,
        settling_time,
        auto_start_delay,
        next_id,
        next_type,
        auto_start_next,
    ):
        """
        Configures/sets a kinematic motion.
        """
        position_target_low = position_target & 0xFF
        position_target_high = position_target >> 8 & 0xFF
        settling_time_low = settling_time & 0xFF
        settling_time_high = settling_time >> 8 & 0xFF
        next_type_auto = next_id << 3 + next_type << 1 + auto_start_next
        self.write_registers(
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

    def close(self):
        """
        Closes the Modbus connection.
        """
        self.client.close()
