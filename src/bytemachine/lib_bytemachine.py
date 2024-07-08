from src.orca.constants import OrcaConstants
from src.orca.actuator import OrcaActuator

ORCA_CONSTANTS = OrcaConstants()


async def configure_two_point_kinematic_motion(
    actuator: OrcaActuator,
    stroke_rate_mm_s: float,
    stroke_length_mm: float,
    stroke_start_offset_mm: float = 0,
) -> None:
    """
    Configures a two-point kinematic motion on the actuator to achieve the
    specified stroke rate and stroke length.

    This method sets up two kinematic motions:
    - Motion 1: Moves the actuator forward by stroke_length_mm.
    - Motion 2: Moves the actuator backward to the starting position.

    To handle smooth changes to motion profiles four kinematic registers are
    used (0, 1, 2, 3) where we swap between using [0, 1] and [2, 3].

    The settling time for each motion is calculated to achieve the desired
    stroke rate.

    Args:
        actuator: The OrcaActuator object representing the actuator.
        stroke_rate_mm_s (float): The desired stroke rate in millimeters per
            second.
        stroke_length_mm (float): The desired stroke length in millimeters.
        stroke_start_offset_mm (float): The desired start position for the
            motion in millimeters (default: 0).
        motion_id_1 (int): The ID of the first kinematic motion (default: 0).
        motion_id_2 (int): The ID of the second kinematic motion (default: 1).

    Returns:
        Union[bool, bool]: A tuple containing two boolean values.
        The first value indicates if setting the first kinematic motion was
        successful. The second value indicates if setting the second
        kinematic motion was successful.
    """
    # Calculate settling time in milliseconds for the given stroke rate.
    settling_time_ms: int = max(int((stroke_length_mm / stroke_rate_mm_s) * 1000), 0)
    # Calculate the start position target in micrometers.
    position_target_start_um: int = max(int(stroke_start_offset_mm * 1000), 0)
    # Calculate end position target in micrometers.
    position_target_end_um: int = max(
        int(stroke_length_mm * 1000 + stroke_start_offset_mm * 1000), 0
    )
    # Configure registers and trigger configured motion.
    while True:
        kin_status = await actuator.motor_read_stream(
            ORCA_CONSTANTS.KINEMATIC_STATUS, register_width=1
        )
        if kin_status:
            active_motion_id = kin_status.register_value & 0x7FFF
            motion_out_id = 0
            motion_in_id = 1
            if active_motion_id == 0 or active_motion_id == 1:
                motion_out_id = 2
                motion_in_id = 3
            motion_to_trigger_id = motion_out_id
            if active_motion_id == 1 or active_motion_id == 3:
                motion_to_trigger_id = motion_in_id
            set_motion_out_successful = await actuator.set_kinematic_motion(
                motion_id=motion_out_id,
                position_target_um=position_target_end_um,
                settling_time_ms=settling_time_ms,
                auto_start_delay_ms=0,
                next_id=motion_in_id,
                motion_type=1,  # Min jerk.
                auto_start_next=1,
            )
            print(f"Set motion out to motion_id {motion_out_id}")
            set_motion_in_successful = await actuator.set_kinematic_motion(
                motion_id=motion_in_id,
                position_target_um=position_target_start_um,
                settling_time_ms=settling_time_ms,
                auto_start_delay_ms=0,
                next_id=motion_out_id,
                motion_type=1,  # Min jerk.
                auto_start_next=1,
            )
            print(f"Set motion in to motion_id {motion_out_id}")
            print(
                f"Sets successful = {set_motion_out_successful and set_motion_in_successful}"
            )
            print(
                f"Active motion id {active_motion_id} triggering just set motion id {motion_to_trigger_id}"
            )
            await actuator.trigger_kinematic_motion(motion_to_trigger_id)
            break
    return


async def auto_zero_wait(
    actuator: OrcaActuator,
    max_force_n: int = 50,
    exit_to_mode: int = ORCA_CONSTANTS.MODE_SLEEP,
) -> bool:
    """
    Auto-zeros the actuator and waits until the actuator exits auto-zero mode.

    Args:
        actuator (OrcaActuator): The OrcaActuator object representing the
            actuator.
        max_force_n (int): The maximum allowable force while auto-zeroing in
            newtons.
        exit_to_mode (int): The mode to exit to once auto-zeroing is complete.


    Returns:
        bool: True if auto-zero was successful and the actuator exited
        auto-zero mode, False otherwise.
    """
    initiate_auto_zero_successful = await actuator.command_auto_zero(
        max_force_n=max_force_n,
        exit_to_mode=exit_to_mode,
    )
    if not initiate_auto_zero_successful:
        print("Failed to initiate auto-zero.")
        return False

    while True:
        mode = await actuator.get_mode()
        if mode is None:
            print("Failed to read actuator mode.")
            return False
        if mode != ORCA_CONSTANTS.MODE_AUTO_ZERO:
            break
    return True
