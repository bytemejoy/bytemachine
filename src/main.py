from typing import Union, Tuple
import asyncio

import pynput

from src.orca.actuator import OrcaActuator
from src.orca.constants import OrcaConstants
from src.bytemachine import lib_bytemachine

ORCA_CONSTANTS = OrcaConstants()

# Default values
STROKE_LENGTH_MM = 0  # Starting stroke length
STROKE_RATE_MM_S = 0  # Starting stroke rate

# Limits
MIN_STROKE_LENGTH_MM = 20
MAX_STROKE_LENGTH_MM = 228
MIN_STROKE_RATE_MM_S = 20
MAX_STROKE_RATE_MM_S = 676

# Increments
STROKE_LENGTH_INCREMENT_MM = 20
STROKE_RATE_INCREMENT_MM_S = 20


def print_usage():
    """Prints current state and usage instructions"""
    print(
        f"Current stroke length {STROKE_LENGTH_MM}mm, stroke rate "
        f"{STROKE_RATE_MM_S}mm/s\n"
        "  Usage:\n"
        "  - up-arrow: increase stroke rate\n"
        "  - down-arrow: decrease stroke rate\n"
        "  - left-arrow: decrease stroke length\n"
        "  - right-arrow: increase stroke length\n"
        "  - escape: exit"
    )


def get_keys_queue():
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def on_press(
        key: Union[pynput.keyboard.KeyCode, pynput.keyboard.Key, None]
    ) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, key)

    pynput.keyboard.Listener(on_press=on_press, suppress=True).start()
    return queue


async def handle_state_change(
    actuator: OrcaActuator, stroke_rate_mm_s, stroke_length_mm
) -> Tuple[int, int]:
    current_mode = await actuator.get_mode()
    kinematic_status = await actuator.read_register(ORCA_CONSTANTS.KINEMATIC_STATUS)
    if not kinematic_status:
        return 0, 0
    should_trigger_motion = not bool((kinematic_status[0] & 0x8000) >> 15)
    success = True
    if current_mode:
        if (
            stroke_length_mm == 0 or stroke_rate_mm_s == 0
        ) and current_mode != ORCA_CONSTANTS.MODE_SLEEP:
            success = await actuator.set_mode(ORCA_CONSTANTS.MODE_SLEEP) and success
            should_trigger_motion = False
        if (
            stroke_length_mm > 0 or stroke_rate_mm_s > 0
        ) and current_mode != ORCA_CONSTANTS.MODE_KINEMATIC:
            success = await actuator.set_mode(ORCA_CONSTANTS.MODE_KINEMATIC) and success
    result_stroke_rate_mm_s = max(stroke_rate_mm_s, MIN_STROKE_RATE_MM_S)
    result_stroke_length_mm = max(stroke_length_mm, MIN_STROKE_LENGTH_MM)
    success = (
        await lib_bytemachine.configure_two_point_kinematic_motion(
            actuator,
            stroke_rate_mm_s=result_stroke_rate_mm_s,
            stroke_length_mm=result_stroke_length_mm,
            stroke_start_offset_mm=35,
        )
        and success
    )
    if should_trigger_motion:
        success = await actuator.trigger_kinematic_motion(motion_id=0) and success
    return result_stroke_rate_mm_s, result_stroke_length_mm


async def main():
    """Main entry point for the Orca actuator control script."""
    key_queue = get_keys_queue()
    actuator = OrcaActuator(port="/dev/tty.usbserial-FT8F0SP7")
    connected = await actuator.connect()
    if not connected:
        print("Failed to connect to the actuator. Exiting.")
        return

    await actuator.set_mode(ORCA_CONSTANTS.MODE_SLEEP)
    await actuator.reset_kinematic_config()
    await actuator.reset_user_options()

    # Perform auto-zero before starting
    print("Performing auto-zero...")
    auto_zero_success = await lib_bytemachine.auto_zero_wait(actuator)
    if not auto_zero_success:
        print("Auto-zero failed. Exiting.")
        return
    print("Auto-zero complete.")

    # Configure max force.
    await actuator.set_max_force(35585)

    async def handle_key(
        key: Union[pynput.keyboard.KeyCode, pynput.keyboard.Key, None]
    ) -> bool:
        """Handles key presses for adjusting stroke length and speed."""
        global STROKE_LENGTH_MM, STROKE_RATE_MM_S
        changed: bool = False
        try:
            if key == pynput.keyboard.Key.left:
                STROKE_LENGTH_MM = max(
                    STROKE_LENGTH_MM - STROKE_LENGTH_INCREMENT_MM,
                    MIN_STROKE_LENGTH_MM,
                )
                changed = True
            elif key == pynput.keyboard.Key.right:
                STROKE_LENGTH_MM = min(
                    STROKE_LENGTH_MM + STROKE_LENGTH_INCREMENT_MM,
                    MAX_STROKE_LENGTH_MM,
                )
                changed = True
            elif key == pynput.keyboard.Key.up:
                STROKE_RATE_MM_S = min(
                    STROKE_RATE_MM_S + STROKE_RATE_INCREMENT_MM_S,
                    MAX_STROKE_RATE_MM_S,
                )
                changed = True
            elif key == pynput.keyboard.Key.down:
                STROKE_RATE_MM_S = max(
                    STROKE_RATE_MM_S - STROKE_RATE_INCREMENT_MM_S,
                    MIN_STROKE_RATE_MM_S,
                )
                changed = True
            elif key == pynput.keyboard.Key.esc:
                return True
            else:
                print(f"Unhandeled key pressed: {key}")

            if changed:
                handle_state_success = await handle_state_change(
                    actuator, STROKE_RATE_MM_S, STROKE_LENGTH_MM
                )
                if not handle_state_success:
                    return True
                STROKE_RATE_MM_S = handle_state_success[0]
                STROKE_LENGTH_MM = handle_state_success[1]
                print_usage()

        except AttributeError:
            print(f"Special key pressed: {key}")
        return False

    # Print current state and usage instructions.
    print_usage()

    while True:
        key = await key_queue.get()
        should_exit = await handle_key(key)
        if should_exit:
            await actuator.set_mode(ORCA_CONSTANTS.MODE_SLEEP)
            break
    actuator.close()


if __name__ == "__main__":
    asyncio.run(main())
