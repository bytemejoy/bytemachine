from pymodbus.client.serial import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.framer import Framer

from src.orca.manage_high_speed_stream import manage_high_speed_stream
from src.orca.motor_command_stream import motor_command_stream
from src.orca.motor_read_stream import motor_read_stream
from src.orca.motor_write_stream import motor_write_stream


class OrcaActuator:
    """
    Class representing an Orca Series Modbus RTU actuator.
    """

    def __init__(self, port, timeout=1):
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
        self.client.connect()

    def read_register(self, address, count=1):
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
                address, count, unit=self.slave_address
            )
            if response.isError():
                print(f"Error reading register(s): {response}")
                return None
            return response.registers
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return None

    def write_register(self, address, value):
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
                address, value, unit=self.slave_address
            )
            if response.isError():
                print(f"Error writing register: {response}")
                return False
            return True
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return False

    def write_registers(self, address, values):
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
                address, values, unit=self.slave_address
            )
            if response.isError():
                print(f"Error writing registers: {response}")
                return False
            return True
        except ModbusIOException as e:
            print(f"Modbus IO Error: {e}")
            return False

    # Custom Modbus function code implementations
    def manage_high_speed_stream(self, enable, baud_rate, delay_us):
        """
        Manages the high-speed stream parameters of the actuator.

        Args:
            enable (bool): True to enable the high-speed stream, False to disable.
            baud_rate (int): The target baud rate for the high-speed stream (bps).
            delay_us (int): The target response delay for the high-speed stream (microseconds).

        Returns:
            tuple: A tuple containing the realized baud rate and delay, or None if the operation failed.
        """
        return manage_high_speed_stream(
            self.client, self.slave_address, enable, baud_rate, delay_us
        )

    def motor_command_stream(self, sub_function_code, data):
        """
        Sends a motor command stream message to the actuator.

        Args:
            sub_function_code (int): The sub-function code specifying the desired operation mode.
            data (int or list): The data associated with the command (e.g., force or position target).

        Returns:
            tuple: A tuple containing the shaft position, realized force, power consumption,
                   temperature, voltage, errors, or None if the operation failed.
        """
        return motor_command_stream(
            self.client, self.slave_address, sub_function_code, data
        )

    def motor_read_stream(self, register_address, register_width):
        """
        Reads a register value from the actuator using the motor read stream function.

        Args:
            register_address (int): The address of the register to read.
            register_width (int): The width of the register (1 for single, 2 for double).

        Returns:
            tuple: A tuple containing the register value, shaft position, realized force, power consumption,
                   temperature, voltage, errors, or None if the operation failed.
        """
        return motor_read_stream(
            self.client, self.slave_address, register_address, register_width
        )

    def motor_write_stream(self, register_address, register_width, data):
        """
        Writes a value to a register in the actuator using the motor write stream function.

        Args:
            register_address (int): The address of the register to write to.
            register_width (int): The width of the register (1 for single, 2 for double).
            data (int): The data to write to the register.

         Returns:
            tuple: A tuple containing the shaft position, realized force, power consumption,
                   temperature, voltage, errors, or None if the operation failed.
        """
        return motor_write_stream(
            self.client, self.slave_address, register_address, register_width, data
        )

    def close(self):
        """
        Closes the Modbus connection.
        """
        self.client.close()
