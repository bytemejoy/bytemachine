from typing import Union

import numpy as np
from pymodbus.client.serial import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.framer import Framer
from pymodbus.pdu import ModbusResponse

from src.orca import bit_utils
from src.orca.constants import OrcaConstants
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

ORCA_CONSTANTS = OrcaConstants()


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

    async def get_serial_number(
        self,
    ) -> Union[int, None]:
        """Get the actuator serial number."""
        read_result: Union[list, None] = await self.read_register(
            ORCA_CONSTANTS.SERIAL_NUMBER_LOW, count=2
        )
        if read_result:
            return bit_utils.combine_low_high(
                np.uint16(read_result[0]), np.uint16(read_result[1])
            )

    async def get_firmware_version(self) -> Union[str, None]:
        """Returns the semantic versioning firmware version."""
        read_result: Union[list, None] = await self.read_register(
            ORCA_CONSTANTS.MAJOR_VERSION, count=3
        )
        if read_result:
            return f"{read_result[0]}.{read_result[1]}.{read_result[2]}"

    async def set_mode(self, mode: int) -> bool:
        """Set actuator mode."""
        return await self.write_register(ORCA_CONSTANTS.CTRL_REG_3, mode)

    async def get_mode(
        self,
    ) -> Union[int, None]:
        """Get the current actuator mode."""
        read_result: Union[list, None] = await self.read_register(
            ORCA_CONSTANTS.MODE_OF_OPERATION
        )
        if read_result:
            return read_result[0]

    async def set_max_force(self, max_force: int) -> bool:
        """Sets the user defined max force."""
        return await self.write_register(ORCA_CONSTANTS.USER_MAX_FORCE, max_force)

    async def set_max_temp(self, max_temp: int) -> bool:
        """Sets the user defined max temp."""
        return await self.write_register(ORCA_CONSTANTS.USER_MAX_TEMP, max_temp)

    async def set_max_power(self, max_power: int) -> bool:
        """Sets the user defined max power."""
        return await self.write_register(ORCA_CONSTANTS.USER_MAX_POWER, max_power)

    async def set_safety_damping(self, max_safety_damping: int) -> bool:
        """Sets the safety motion damping gain."""
        return await self.write_register(
            ORCA_CONSTANTS.SAFETY_DGAIN, max_safety_damping
        )

    async def trigger_kinematic_motion(self, motion_id: int) -> bool:
        """Trigger a kinematic motion."""
        return await self.write_register(ORCA_CONSTANTS.KIN_SW_TRIGGER, motion_id)

    async def full_reset(self) -> bool:
        """Full reset of the actuator."""
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_FULL_RESET
        )

    async def clear_erros(self) -> bool:
        """Clears all active and latched erros."""
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_CLEAR_ERRORS
        )

    async def invert_position(self) -> bool:
        """Change the direction of positive movement."""
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_INVERT_POSITION
        )

    async def save_params(self) -> bool:
        """
        Save the parameter section of registers (400 - 419) to flash memory.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_PARAMS
        )

    async def save_tuning(self) -> bool:
        """
        Save the tuning section of registers (128-153) to flash memory.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_TUNING
        )

    async def save_user_options(self) -> bool:
        """
        Save the user options section of registers (160 - 178) to flash memory.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_USER_OPTS
        )

    async def save_kinematic_config(self) -> bool:
        """
        Save the kinematic section of registers (778 - 973) to flash memory.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_KINEMATIC_CONFIG
        )

    async def save_haptic_config(self) -> bool:
        """
        Save the haptic section of registers (640 - 674) to flash memory.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_HAPTIC_CONFIG
        )

    async def reset_params(self) -> bool:
        """
        Reset the parameter section of registers (400 - 419) to defaults.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4, ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_PARAMS
        )

    async def reset_tuning(self) -> bool:
        """
        Reset the tuning section of registers (128-153) to defaults.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4, ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_TUNING
        )

    async def reset_user_options(self) -> bool:
        """
        Reset the user options section of registers (160 - 178) to defaults.
        """
        write_successful: bool = await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4,
            ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_MOTOR_USER_OPTS,
        )
        return (
            await self.write_register(
                ORCA_CONSTANTS.CTRL_REG_4,
                ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_MODBUS_USER_OPTS,
            )
            & write_successful
        )

    async def reset_kinematic_config(self) -> bool:
        """
        Reset the kinematic section of registers (778 - 973) to defaults.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4,
            ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_KINEMATIC_CONFIG,
        )

    async def reset_haptic_config(self) -> bool:
        """
        Reset the haptic section of registers (640 - 674) to defaults.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4,
            ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_HAPTIC_CONFIG,
        )

    async def zero_position(self) -> bool:
        """Sets the current shaft position as the zero point."""
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_ZERO_POSITION
        )

    async def auto_zero(self, max_force: int, exit_to_mode: int) -> bool:
        """
        Auto zeros the actuator using up to max_force and exiting to mode exit_to_mode when complete.
        """
        write_successful: bool = await self.write_registers(
            ORCA_CONSTANTS.ZERO_MODE,
            [ORCA_CONSTANTS.AUTO_ZERO_MODE_ENABLED, max_force, exit_to_mode],
        )
        return (
            await self.write_register(
                ORCA_CONSTANTS.CTRL_REG_3, ORCA_CONSTANTS.MODE_AUTO_ZERO
            )
            & write_successful
        )

    async def set_kinematic_motion(
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
        Set a kinematic motion.
        """
        position_target_int32: np.int32 = np.int32(position_target)
        position_target_low: int = bit_utils.get_lsb(position_target_int32)
        position_target_high: int = bit_utils.get_msb(position_target_int32)
        settling_time_int32: np.int32 = np.int32(settling_time)
        settling_time_low: int = bit_utils.get_lsb(settling_time_int32)
        settling_time_high: int = bit_utils.get_lsb(settling_time_int32)
        next_type_auto: int = (motion_type << 1) | (next_id << 3) | auto_start_next
        return await self.write_registers(
            ORCA_CONSTANTS.KIN_MOTION_0 + 6 * motion_id,
            [
                position_target_low,
                position_target_high,
                settling_time_low,
                settling_time_high,
                auto_start_delay,
                next_type_auto,
            ],
        )

    async def set_spring_effect(
        self,
        spring_id: int,
        gain: int,
        center: int,
        dead_zone: int,
        saturation: int,
        coupling: int,
    ) -> bool:
        """
        Set a spring effect.
        """
        gain_low: int = bit_utils.get_lsb(np.int32(gain))
        center_int32: np.int32 = np.int32(center)
        center_low: int = bit_utils.get_lsb(center_int32)
        center_high: int = bit_utils.get_msb(center_int32)
        coupling_low: int = bit_utils.get_lsb(np.int32(coupling))
        dead_zone_low: int = bit_utils.get_lsb(np.int32(dead_zone))
        saturation_low: int = bit_utils.get_lsb(np.int32(saturation))
        return await self.write_registers(
            ORCA_CONSTANTS.S0_GAIN_N_MM + 6 * spring_id,
            [
                gain_low,
                center_low,
                center_high,
                coupling_low,
                dead_zone_low,
                saturation_low,
            ],
        )

    async def set_oscillation_effect(
        self,
        oscillation_id: int,
        amplitude: int,
        frequency: int,
        duty: int,
        waveform_type: int,
    ) -> bool:
        """
        Set an oscillation effect.
        """
        amplitude_low: int = bit_utils.get_lsb(np.int32(amplitude))
        waveform_type_low: int = bit_utils.get_lsb(np.int32(waveform_type))
        frequency_low: int = bit_utils.get_lsb(np.int32(frequency))
        duty_low: int = bit_utils.get_lsb(np.int32(duty))
        return await self.write_registers(
            ORCA_CONSTANTS.O0_GAIN_N + 4 * oscillation_id,
            [
                amplitude_low,
                waveform_type_low,
                frequency_low,
                duty_low,
            ],
        )

    async def set_position_tuning(
        self,
        proportional_gain: int,
        integral_gain: int,
        derivative_velocity_gain: int,
        saturation: int,
        derivative_error_gain: int = 0,
    ) -> bool:
        """
        Set the position controller (PID) tuning.
        """
        proportional_gain_low: int = bit_utils.get_lsb(np.int32(proportional_gain))
        integral_gain_low: int = bit_utils.get_lsb(np.int32(integral_gain))
        derivative_velocity_gain_low: int = bit_utils.get_lsb(
            np.int32(derivative_velocity_gain)
        )
        derivative_error_gain_low: int = bit_utils.get_lsb(
            np.int32(derivative_error_gain)
        )
        saturation_int32: np.int32 = np.int32(saturation)
        saturation_low: int = bit_utils.get_lsb(saturation_int32)
        saturation_high: int = bit_utils.get_msb(saturation_int32)
        write_successful: bool = await self.write_registers(
            ORCA_CONSTANTS.PC_PGAIN,
            [
                proportional_gain_low,
                integral_gain_low,
                derivative_velocity_gain_low,
                derivative_error_gain_low,
                saturation_low,
                saturation_high,
            ],
        )
        return (
            await self.write_register(
                ORCA_CONSTANTS.CTRL_REG_1,
                ORCA_CONSTANTS.CTRL_REG_1_SET_POSITION_CONTROLLER_GAIN,
            )
            & write_successful
        )

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

    def close(self) -> None:
        """
        Closes the Modbus connection.
        """
        self.client.close()
