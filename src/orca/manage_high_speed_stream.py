from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


def manage_high_speed_stream(client, slave_address, enable, baud_rate, delay_us):
    """
    Manages the high-speed stream parameters of the Orca actuator.

    Args:
        client: The Modbus client object.
        slave_address (int): The Modbus slave address of the actuator.
        enable (bool): True to enable the high-speed stream, False to disable.
        baud_rate (int): The target baud rate for the high-speed stream (bps).
        delay_us (int): The target response delay for the high-speed stream (microseconds).

    Returns:
        tuple: A tuple containing the realized baud rate and delay, or None if the operation failed.
    """
    sub_function_code = 0xFF00 if enable else 0x0000
    request = client.write_registers(
        1,
        [sub_function_code, baud_rate, delay_us],
        unit=slave_address,
        function_code=65,  # Custom function code 65 (0x41)
    )

    if request.isError():
        print(f"Error managing high-speed stream: {request}")
        return None

    response = client.read_holding_registers(1, 3, unit=slave_address, function_code=65)
    if response.isError():
        print(f"Error reading high-speed stream response: {response}")
        return None

    decoder = BinaryPayloadDecoder.fromRegisters(
        response.registers, byteorder=Endian.BIG
    )
    realized_baud_rate = decoder.decode_32bit_int()
    realized_delay_us = decoder.decode_16bit_uint()

    return realized_baud_rate, realized_delay_us
