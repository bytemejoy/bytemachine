from src.orca.actuator import OrcaActuator


def main():
    """A collection of sample interactions with an OrcaActuator."""
    actuator = OrcaActuator(
        port="/dev/tty.usbserial-FT8F0SP7"
    )  # TODO(bytemejoy): Write auto port config logic

    # Auto zero out the motor.
    actuator.auto_zero(50, 1)

    # Close the Modbus connection
    actuator.close()


if __name__ == "__main__":
    main()
