import asyncio

from pynput import keyboard

from src.orca.actuator import OrcaActuator
from src.orca.constants import OrcaConstants
from src.bytemachine import lib_bytemachine

ORCA_CONSTANTS = OrcaConstants()

# Default values
STROKE_LENGTH_MM = 0  # Starting stroke length
STROKE_RATE_MM_S = 0  # Starting stroke rate

# Limits
MIN_STROKE_LENGTH_MM = 0
MAX_STROKE_LENGTH_MM = 228
MIN_STROKE_RATE_MM_S = 0
MAX_STROKE_RATE_MM_S = 676

# Increments
STROKE_LENGTH_INCREMENT_MM = 25
STROKE_RATE_INCREMENT_MM_S = 33


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


async def handle_state_change(
    actuator: OrcaActuator, stroke_rate_mm_s, stroke_length_mm
):
    current_mode = await actuator.get_mode()
    should_trigger = False
    if current_mode:
        if (
            stroke_length_mm == 0 or stroke_rate_mm_s == 0
        ) and current_mode != ORCA_CONSTANTS.MODE_SLEEP:
            await actuator.set_mode(ORCA_CONSTANTS.MODE_SLEEP)
        if (
            stroke_length_mm > 0 or stroke_rate_mm_s > 0
        ) and current_mode != ORCA_CONSTANTS.MODE_KINEMATIC:
            await actuator.set_mode(ORCA_CONSTANTS.MODE_KINEMATIC)
            should_trigger = True
    await lib_bytemachine.configure_two_point_kinematic_motion(
        actuator,
        stroke_rate_mm_s=stroke_rate_mm_s,
        stroke_length_mm=stroke_length_mm,
    )
    if should_trigger:
        await actuator.trigger_kinematic_motion(motion_id=0)


async def main():
    """Main entry point for the Orca actuator control script."""
    actuator = OrcaActuator(port="/dev/tty.usbserial-FT8F0SP7")
    connected = await actuator.connect()
    if not connected:
        print("Failed to connect to the actuator. Exiting.")
        return

    # Perform auto-zero before starting
    print("Performing auto-zero...")
    auto_zero_success = await lib_bytemachine.auto_zero_wait(actuator)
    if not auto_zero_success:
        print("Auto-zero failed. Exiting.")
        return
    print("Auto-zero complete.")

    def on_press(key):
        """Handles key presses for adjusting stroke length and speed."""
        global STROKE_LENGTH_MM, STROKE_RATE_MM_S
        changed: bool = False
        try:
            if key == keyboard.Key.left:
                STROKE_LENGTH_MM = max(
                    STROKE_LENGTH_MM - STROKE_LENGTH_INCREMENT_MM,
                    MIN_STROKE_LENGTH_MM,
                )
                changed = True
            elif key == keyboard.Key.right:
                STROKE_LENGTH_MM = min(
                    STROKE_LENGTH_MM + STROKE_LENGTH_INCREMENT_MM,
                    MAX_STROKE_LENGTH_MM,
                )
                changed = True
            elif key == keyboard.Key.up:
                STROKE_RATE_MM_S = min(
                    STROKE_RATE_MM_S + STROKE_RATE_INCREMENT_MM_S,
                    MAX_STROKE_RATE_MM_S,
                )
                changed = True
            elif key == keyboard.Key.down:
                STROKE_RATE_MM_S = max(
                    STROKE_RATE_MM_S - STROKE_RATE_INCREMENT_MM_S,
                    MIN_STROKE_RATE_MM_S,
                )
                changed = True

            if changed:
                asyncio.create_task(
                    handle_state_change(actuator, STROKE_RATE_MM_S, STROKE_LENGTH_MM)
                )
                print_usage()

        except AttributeError:
            print("Invalid key pressed: {0}".format(key))
            print_usage()

    def on_release(key):
        """Handles key releases."""
        if key == keyboard.Key.esc:
            # Stop listener and exit the script
            return

    # Print current state and
    print_usage()

    # Collect events until esc is pressed.
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    actuator.close()


if __name__ == "__main__":
    asyncio.run(main())
