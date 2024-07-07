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
    Class representing an Orca actuator.

    This class provides methods for interacting with an Orca actuator over a Modbus RTU
    connection. It allows you to:

    - Connect to the actuator
    - Configure the Modbus stream (standard/high-speed)
    - Read from and write to actuator registers
    - Control actuator configuration
    - Command position, force, kinematic motions, and haptic effects
    - Configure spring and oscillation effects
    - Tune the position (PID) controller

    Attributes:
        framer (Framer): The Modbus framer to use (default: Framer.RTU).
        port (str): The serial port the actuator is connected to.
        slave_address (int): The slave address of the actuator (default: 1).
        baudrate (int): The baud rate of the serial connection (default: 19200).
        timeout_s (int): The timeout for Modbus requests in seconds (default: 1).
        stop_bits (int): The number of stop bits to use (default: 1).
        parity (str): The parity to use (default: "E" for even parity).
        client (AsyncModbusSerialClient): The asynchronous Modbus serial client object.
    """

    def __init__(self, port: str, timeout: int = 1):
        """
        Initializes the OrcaActuator object.

        Args:
            port (str): The serial port the actuator is connected to.
            timeout_s (int): The timeout for Modbus requests in seconds (default: 1).
        """
        self.framer: Framer = Framer.RTU
        self.port: str = port
        self.slave_address: int = 1
        self.baudrate: int = 19200
        self.timeout_s: int = timeout
        self.stop_bits: int = 1
        self.parity: str = "E"
        self.client: AsyncModbusSerialClient = AsyncModbusSerialClient(
            framer=self.framer,
            port=self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stop_bits,
            timeout=self.timeout_s,
        )
        # Orca actuators use a default interval of 2ms.
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
        """
        Get the actuator serial number.

        Returns:
            Union[int, None]: The actuator serial number, or None if reading failed.
        """
        read_result: Union[list, None] = await self.read_register(
            ORCA_CONSTANTS.SERIAL_NUMBER_LOW, count=2
        )
        if read_result:
            return bit_utils.combine_low_high(
                np.uint16(read_result[0]), np.uint16(read_result[1])
            )

    async def get_firmware_version(self) -> Union[str, None]:
        """
        Returns the semantic versioning firmware version.

        Returns:
            Union[str, None]: The firmware version string (e.g., "1.2.3"), or None if
                reading failed.
        """
        read_result: Union[list, None] = await self.read_register(
            ORCA_CONSTANTS.MAJOR_VERSION, count=3
        )
        if read_result:
            return f"{read_result[0]}.{read_result[1]}.{read_result[2]}"

    async def set_mode(self, mode: int) -> bool:
        """
        Set actuator mode.

        Args:
            mode (int): The desired actuator mode. Valid modes are:
                * 1  (SLEEP)
                * 2  (FORCE)
                * 3  (POSITION)
                * 4  (MODE_HAPTIC)
                * 5  (MODE_KINEMATIC)
                * 55 (MODE_AUTO_ZERO)

        Returns:
            bool: True if the mode was set successfully, False otherwise.
        """
        return await self.write_register(ORCA_CONSTANTS.CTRL_REG_3, mode)

    async def get_mode(
        self,
    ) -> Union[int, None]:
        """
        Get the current actuator mode.

        Returns:
            Union[int, None]: The current actuator mode, or None if reading failed.
        """
        read_result: Union[list, None] = await self.read_register(
            ORCA_CONSTANTS.MODE_OF_OPERATION
        )
        if read_result:
            return read_result[0]

    async def set_max_force(self, max_force_mn: int) -> bool:
        """
        Sets the user defined max force in millinewtons.

        The motor has no default maximum force threshold, but one can be set
        which will limit forces beyond this level. Setting the register to zero
        disables this threshold.

        Args:
            max_force_mn (int): The maximum force in millinewtons.

        Returns:
            bool: True if the max force was set successfully, False otherwise.
        """
        max_force_int32 = np.int32(max_force_mn)
        max_force_low = bit_utils.get_lsb(max_force_int32)
        max_force_high = bit_utils.get_msb(max_force_int32)
        return await self.write_registers(
            ORCA_CONSTANTS.USER_MAX_FORCE, [max_force_low, max_force_high]
        )

    async def set_max_temp(self, max_temp_c: int) -> bool:
        """
        Sets the user defined max temp in degrees celsius.

        The motor will have a maximum temperature at which it will shut off. A
        lower temperature can be set to cause the motor to shut down at a lower
        temperature. The temperature shutoff threshold cannot be disabled or
        raised beyond the default maximum temperature.

        Args:
            max_temp_c (int): The maximum temperature in degrees celsius.

        Returns:
            bool: True if the max temp was set successfully, False otherwise.
        """
        return await self.write_register(ORCA_CONSTANTS.USER_MAX_TEMP, max_temp_c)

    async def set_max_power(self, max_power_w: int) -> bool:
        """
        Sets the user defined max power in watts.

        If the power burned in the motor exceeds this or the device’s default
        threshold, the drivers will be disabled, preventing power draw. Setting
        this register to zero or higher than the default setting will result in
        the motor only powering down when unsafe levels are reached.

        When the power burned in the stator exceeds the device or user-set
        maximum value, a Power Exceeded error is asserted. This error is
        cleared by commanding the motor into Sleep Mode (1). If this error is
        experienced, either the maximum power user setting can be increased, or
        the maximum force user setting should be decreased. If the position
        controller (i.e., Position Mode (3)) is causing this error, the
        saturation level can also be decreased to prevent this error.

        Args:
            max_power_w (int): The maximum power in watts.

        Returns:
            bool: True if the max power was set successfully, False otherwise.
        """
        return await self.write_register(ORCA_CONSTANTS.USER_MAX_POWER, max_power_w)

    async def set_safety_damping(self, max_safety_damping: int) -> bool:
        """
        Sets the safety motion damping gain value used when communications are
        interrupted.

        Args:
            max_safety_damping (int): The safety motion damping gain.

        Returns:
            bool: True if the safety damping was set successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.SAFETY_DGAIN, max_safety_damping
        )

    async def trigger_kinematic_motion(self, motion_id: int) -> bool:
        """
        Trigger a kinematic motion.

        Args:
            motion_id (int): The ID of the kinematic motion to trigger.

        Returns:
            bool: True if the motion was triggered successfully, False otherwise.
        """
        return await self.write_register(ORCA_CONSTANTS.KIN_SW_TRIGGER, motion_id)

    async def full_reset(self) -> bool:
        """
        Full reset of the actuator.

        Returns:
            bool: True if the reset was successful, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_FULL_RESET
        )

    async def clear_erros(self) -> bool:
        """
        Clears all active and latched errors.

        Returns:
            bool: True if the errors were cleared successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_CLEAR_ERRORS
        )

    async def invert_position(self) -> bool:
        """
        Change the direction of positive movement.

        Returns:
            bool: True if the position inversion was successful, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_INVERT_POSITION
        )

    async def save_params(self) -> bool:
        """
        Save the parameter section of registers (400 - 419) to flash memory.

        Returns:
            bool: True if the parameters were saved successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_PARAMS
        )

    async def save_tuning(self) -> bool:
        """
        Save the tuning section of registers (128-153) to flash memory.

        Returns:
            bool: True if the tuning was saved successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_TUNING
        )

    async def save_user_options(self) -> bool:
        """
        Save the user options section of registers (160 - 178) to flash memory.

        Returns:
            bool: True if the user options were saved successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_USER_OPTS
        )

    async def save_kinematic_config(self) -> bool:
        """
        Save the kinematic section of registers (778 - 973) to flash memory.

        Returns:
            bool: True if the kinematic configuration was saved successfully, False
                otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_KINEMATIC_CONFIG
        )

    async def save_haptic_config(self) -> bool:
        """
        Save the haptic section of registers (640 - 674) to flash memory.

        Returns:
            bool: True if the haptic configuration was saved successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_2, ORCA_CONSTANTS.CTRL_REG_2_SAVE_HAPTIC_CONFIG
        )

    async def reset_params(self) -> bool:
        """
        Reset the parameter section of registers (400 - 419) to defaults.

        Returns:
            bool: True if the parameters were reset successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4, ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_PARAMS
        )

    async def reset_tuning(self) -> bool:
        """
        Reset the tuning section of registers (128-153) to defaults.

        Returns:
            bool: True if the tuning was reset successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4, ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_TUNING
        )

    async def reset_user_options(self) -> bool:
        """
        Reset the user options section of registers (160 - 178) to defaults.

        Returns:
            bool: True if the user options were reset successfully, False otherwise.
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

        Returns:
            bool: True if the kinematic configuration was reset successfully, False
                otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4,
            ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_KINEMATIC_CONFIG,
        )

    async def reset_haptic_config(self) -> bool:
        """
        Reset the haptic section of registers (640 - 674) to defaults.

        Returns:
            bool: True if the haptic configuration was reset successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_4,
            ORCA_CONSTANTS.CTRL_REG_4_SET_DEFAULT_HAPTIC_CONFIG,
        )

    async def zero_position(self) -> bool:
        """
        Sets the current shaft position as the zero point.

        Returns:
            bool: True if the position was zeroed successfully, False otherwise.
        """
        return await self.write_register(
            ORCA_CONSTANTS.CTRL_REG_0, ORCA_CONSTANTS.CTRL_REG_0_ZERO_POSITION
        )

    async def command_auto_zero(self, max_force_n: int, exit_to_mode: int) -> bool:
        """
        Initiates the auto zero process using up to max_force_n (newtons) and
        exiting to mode exit_to_mode when complete.

        Args:
            max_force_n (int): The maximum force to use during auto-zero in newtons.
            exit_to_mode (int): The mode to switch to after auto-zero is complete.

        Returns:
            bool: True if auto-zero was initiated successfully, False otherwise.
        """
        write_successful: bool = await self.write_registers(
            ORCA_CONSTANTS.ZERO_MODE,
            [ORCA_CONSTANTS.AUTO_ZERO_MODE_ENABLED, max_force_n, exit_to_mode],
        )
        return (
            await self.write_register(
                ORCA_CONSTANTS.CTRL_REG_3, ORCA_CONSTANTS.MODE_AUTO_ZERO
            )
            & write_successful
        )

    async def command_position(self, position_um: int) -> bool:
        """
        Commands the specified position in micrometers.

        Args:
            position_um (int): The target position in micrometers.

        Returns:
            bool: True if the position command was sent successfully, False otherwise.
        """
        position_int32 = np.int32(position_um)
        position_low = bit_utils.get_lsb(position_int32)
        position_high = bit_utils.get_msb(position_int32)
        return await self.write_registers(
            ORCA_CONSTANTS.MOTOR_COMMAND_POS, [position_low, position_high]
        )

    async def command_force(self, force_mn: int) -> bool:
        """
        Commands the specified force in millinewtons

        Args:
            force_mn (int): The target force in millinewtons.

        Returns:
            bool: True if the force command was sent successfully, False otherwise.
        """
        force_int32 = np.int32(force_mn)
        force_low = bit_utils.get_lsb(force_int32)
        force_high = bit_utils.get_msb(force_int32)
        return await self.write_registers(
            ORCA_CONSTANTS.MOTOR_COMMAND_FORCE, [force_low, force_high]
        )

    async def set_kinematic_motion(
        self,
        motion_id: int,
        position_target_um: int,
        settling_time_ms: int,
        auto_start_delay_ms: int,
        next_id: int,
        motion_type: int,
        auto_start_next: int,
    ) -> bool:
        """
        Set a kinematic motion.

        Args:
            motion_id (int): The ID of the kinematic motion to set.
            position_target_um (int): The target position for the motion in micrometers.
            settling_time_ms (int): The settling time for the motion in milliseconds.
            auto_start_delay_ms (int): The auto start delay for the motion in milliseconds.
            next_id (int): The ID of the next motion to execute.
            motion_type (int): The type of motion.
            auto_start_next (int): Whether to automatically start the next motion.

        Returns:
            bool: True if the kinematic motion was set successfully, False otherwise.
        """
        position_target_int32: np.int32 = np.int32(position_target_um)
        position_target_low: int = bit_utils.get_lsb(position_target_int32)
        position_target_high: int = bit_utils.get_msb(position_target_int32)
        settling_time_int32: np.int32 = np.int32(settling_time_ms)
        settling_time_low: int = bit_utils.get_lsb(settling_time_int32)
        settling_time_high: int = bit_utils.get_msb(settling_time_int32)
        next_type_auto: int = (motion_type << 1) | (next_id << 3) | auto_start_next
        return await self.write_registers(
            ORCA_CONSTANTS.KIN_MOTION_0 + 6 * motion_id,
            [
                position_target_low,
                position_target_high,
                settling_time_low,
                settling_time_high,
                auto_start_delay_ms,
                next_type_auto,
            ],
        )

    async def set_spring_effect(
        self,
        spring_id: int,
        gain_n_mm: int,
        center_um: int,
        dead_zone_mm: int,
        saturation_n: int,
        coupling: int,
    ) -> bool:
        """
        Set a spring effect.

        Args:
            spring_id (int): The ID of the spring effect to set.
            gain_n_mm (int): Rate at which the force will increase proportional to
                the change in position.
            center_um (int): The center position of the spring in micrometers.
            dead_zone_mm (int): The dead zone of the spring in millimeters.
            saturation_n (int): The saturation point of the spring in newtons.
            coupling (int): The coupling of the spring. Valid coupling types:
                * 0 (Both)
                * 1 (Positive)
                * 2 (Negative)

        Returns:
            bool: True if the spring effect was set successfully, False otherwise.
        """
        gain_low: int = bit_utils.get_lsb(np.int32(gain_n_mm))
        center_int32: np.int32 = np.int32(center_um)
        center_low: int = bit_utils.get_lsb(center_int32)
        center_high: int = bit_utils.get_msb(center_int32)
        coupling_low: int = bit_utils.get_lsb(np.int32(coupling))
        dead_zone_low: int = bit_utils.get_lsb(np.int32(dead_zone_mm))
        saturation_low: int = bit_utils.get_lsb(np.int32(saturation_n))
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
        amplitude_n: int,
        frequency_dhz: int,
        duty_percent: int,
        waveform_type: int,
    ) -> bool:
        """
        Set an oscillation effect.

        Args:
            oscillation_id (int): The ID of the oscillation effect to set.
            amplitude_n (int): The amplitude of the oscillation in newtons.
            frequency_dhz (int): The frequency of the oscillation in decihertz.
            duty_percent (int): The duty cycle of the oscillation. This field
                only applies to Pulse waveforms types and indicates what
                percentage of the waveform should be spent in a high state
                (applying positive force) with the remaining percent being in
                the ‘low’ state.
            waveform_type (int): The type of waveform for the oscillation:
                * 0 (square)
                * 1 (sine)
                * 2 (triangle)
                * 3 (sawtooth)

        Returns:
            bool: True if the oscillation effect was set successfully, False otherwise.
        """
        amplitude_low: int = bit_utils.get_lsb(np.int32(amplitude_n))
        waveform_type_low: int = bit_utils.get_lsb(np.int32(waveform_type))
        frequency_low: int = bit_utils.get_lsb(np.int32(frequency_dhz))
        duty_low: int = bit_utils.get_lsb(np.int32(duty_percent))
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
        proportional_gain_mn_um: int,
        integral_gain_mns_um: int,
        derivative_velocity_gain_mnmm_s: int,
        saturation_mn: int,
        derivative_error_gain_mnmm_s: int = 0,
    ) -> bool:
        """
        Set the position controller (PID) tuning.

        Args:
            proportional_gain_mn_um (int): The proportional gain in
                millinewtons per micrometer.
            integral_gain_mns_um (int): The integral gain in millinewtons
                seconds per micrometer.
            derivative_velocity_gain_mnmm_s (int): The derivative velocity gain
                in millinewton millimeters per second.
            saturation_mn (int): The saturation value in millinewtons.
            derivative_error_gain_mnmm_s (int): The derivative error gain in
                millinewton millimeters per second (default: 0).

        Returns:
            bool: True if the position tuning was set successfully, False otherwise.
        """
        proportional_gain_low: int = bit_utils.get_lsb(
            np.int32(proportional_gain_mn_um)
        )
        integral_gain_low: int = bit_utils.get_lsb(np.int32(integral_gain_mns_um))
        derivative_velocity_gain_low: int = bit_utils.get_lsb(
            np.int32(derivative_velocity_gain_mnmm_s)
        )
        derivative_error_gain_low: int = bit_utils.get_lsb(
            np.int32(derivative_error_gain_mnmm_s)
        )
        saturation_int32: np.int32 = np.int32(saturation_mn)
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

        Args:
            enable (bool): True to enable the custom baud_rate and delay_us,
                False to disable.
            baud_rate (int): The baud rate for the high-speed stream.
            delay_us (int): The delay between messages in microseconds for the
                high-speed stream.

        Returns:
            Union[ManageHighSpeedStreamResult, None]: The result of the
                high-speed stream management command, or None if an error
                occurred.
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

        Args:
            sub_function_code (int): The sub-function code for the motor
                command.
            data (int): The data associated with the motor command.

        Returns:
            Union[MotorCommandStreamResult, None]: The result of the motor
                command stream message, or None if an error occurred.
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
        Reads a register value from the actuator using the motor read stream
        function.

        Args:
            register_address (int): The address of the register to read.
            register_width (int): The width of the register in bytes.

        Returns:
            Union[MotorReadStreamResult, None]: The result of the motor read
                stream function, or None if an error occurred.
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
        Writes a value to a register in the actuator using the motor write
        stream function.

        Args:
            register_address (int): The address of the register to write to.
            register_width (int): The width of the register in bytes.
            data (int): The data to write to the register.

        Returns:
            Union[MotorWriteStreamResult, None]: The result of the motor write
                stream function, or None if an error occurred.
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
