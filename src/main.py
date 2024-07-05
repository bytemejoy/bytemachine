import asyncio

from src.orca.actuator import OrcaActuator


async def main():
    """A collection of sample interactions with an OrcaActuator."""
    actuator = OrcaActuator(
        port="/dev/tty.usbserial-FT8F0SP7"
    )  # TODO(bytemejoy): Write auto port config logic

    # Auto zero out the actuator.
    auto_zero_successful = await actuator.auto_zero(50, 1)
    print(f"Auto zero successful = {auto_zero_successful}")

    # Close the Modbus connection
    actuator.close()


if __name__ == "__main__":
    asyncio.run(main())
