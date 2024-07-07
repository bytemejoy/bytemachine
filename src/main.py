import asyncio
import time

from src.orca.actuator import OrcaActuator
from src.orca import constants

ORCA_CONSTANTS = constants.OrcaConstants()


async def main() -> None:
    """A collection of sample interactions with an OrcaActuator."""
    actuator = OrcaActuator(
        port="/dev/tty.usbserial-FT8F0SP7"
    )  # TODO(bytemejoy): Write auto port config logic

    # Connect to the actuator.
    conneciton_success = await actuator.connect()
    print(f"Connected {conneciton_success}")

    # Reset user specified configuration.
    await actuator.reset_user_options()
    await actuator.reset_kinematic_config()

    # Get serial number.
    serial_number = await actuator.get_serial_number()
    if serial_number:
        print(f"Serial number is {serial_number}")

    # Get firmware version.
    firmware_verison = await actuator.get_firmware_version()
    if firmware_verison:
        print(f"Serial number is {firmware_verison}")

    # Auto zero out the actuator.
    await actuator.set_mode(ORCA_CONSTANTS.MODE_SLEEP)
    auto_zero_successful: bool = await actuator.command_auto_zero(
        max_force_n=50, exit_to_mode=ORCA_CONSTANTS.MODE_SLEEP
    )
    while True:
        current_mode = await actuator.get_mode()
        if current_mode and current_mode != ORCA_CONSTANTS.MODE_AUTO_ZERO:
            break
    print(f"Auto zero successful = {auto_zero_successful}")

    # Limit the amount of force the shaft may exert.
    await actuator.set_max_force(max_force_mn=44482)

    # Configure kinematic motion.
    kinematic_write_successful = await actuator.set_kinematic_motion(
        motion_id=0,
        position_target_um=200000,
        settling_time_ms=500,
        auto_start_delay_ms=0,
        next_id=2,
        motion_type=1,
        auto_start_next=1,
    )
    kinematic_write_successful = (
        await actuator.set_kinematic_motion(
            motion_id=1,
            position_target_um=50000,
            settling_time_ms=500,
            auto_start_delay_ms=0,
            next_id=0,
            motion_type=1,
            auto_start_next=1,
        )
        and kinematic_write_successful
    )
    if kinematic_write_successful:
        await actuator.set_mode(ORCA_CONSTANTS.MODE_KINEMATIC)
        triggered = await actuator.trigger_kinematic_motion(motion_id=0)
        print(f"Triggered motion success = {triggered}")

    # Let the kinematic motion run for ten seconds.
    time.sleep(10)

    # Set the mode to sleep.
    await actuator.set_mode(ORCA_CONSTANTS.MODE_SLEEP)

    # Close the Modbus connection
    actuator.close()


if __name__ == "__main__":
    asyncio.run(main())
