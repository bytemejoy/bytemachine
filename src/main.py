from src.orca.actuator import OrcaActuator


def main():
    """A collection of sample interactions with an OrcaActuator."""
    actuator = OrcaActuator(
        port="/dev/ttys3"
    )  # TODO(bytemejoy): Write auto port config logic

    # Read the voltage register (address 338)
    voltage = actuator.read_register(338)
    if voltage is not None:
        print(f"Voltage: {voltage[0]} mV")

    # Set the user max temperature (address 139) to 60 degrees
    success = actuator.write_register(139, 60)
    print(f"Write successful: {success}")

    # Enable high-speed stream with baud rate of 625 kHz and delay of 50 us
    realized_results = actuator.manage_high_speed_stream(
        enable=True, baud_rate=625000, delay_us=50
    )
    if realized_results is not None:
        realized_baud_rate, realized_delay_us = realized_results
        print(f"Realized baud rate: {realized_baud_rate} bps")
        print(f"Realized delay: {realized_delay_us} us")

    # Send a force control stream command to set the target force to 1000 mN
    command_stream_results = actuator.motor_command_stream(
        sub_function_code=0x1C, data=1000
    )
    if command_stream_results is not None:
        position, force, power, temperature, voltage, errors = command_stream_results
        print(f"Position: {position} um")
        print(f"Force: {force} mN")
        print(f"Power: {power} W")
        print(f"Temperature: {temperature} C")
        print(f"Voltage: {voltage} mV")
        print(f"Error register contents: {errors}")

    # Read the user max temperature register (address 139) using motor read stream
    read_stream_results = actuator.motor_read_stream(
        register_address=139, register_width=1
    )
    if read_stream_results is not None:
        print(f"User Max Temp: {read_stream_results[0]}")

    # Write a value of 50 to the user max temperature register using motor write stream
    write_stream_results = actuator.motor_write_stream(
        register_address=139, register_width=1, data=50
    )
    print(f"Write successful: {write_stream_results is not None}")

    # Close the Modbus connection
    actuator.close()


if __name__ == "__main__":
    main()
