from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


def motor_read_stream(client, slave_address, register_address, register_width):
    """
    Reads a register value from the Orca actuator using the motor read stream function.

    Args:
        client: The Modbus client object.
        slave_address (int): The Modbus slave address of the actuator.
        register_address (int): The address of the register to read.
        register_width (int): The width of the register (1 for single, 2 for double).

    Returns:
        tuple: A tuple containing the register value, shaft position, realized force, power consumption,
               temperature, voltage, errors, or None if the operation failed.
    """

    request = client.write_registers(
        1,
        [register_address, register_width],
        unit=slave_address,
        function_code=104,  # Custom function code 104 (0x68)
    )
    if request.isError():
        print(f"Error sending motor read stream: {request}")
        return None

    response = client.read_holding_registers(
        1, 8, unit=slave_address, function_code=104
    )
    if response.isError():
        print(f"Error reading motor read stream response: {response}")
        return None

    decoder = BinaryPayloadDecoder.fromRegisters(
        response.registers, byteorder=Endian.BIG
    )
    register_value = (
        decoder.decode_32bit_int()
        if register_width == 2
        else decoder.decode_16bit_uint()
    )
    position = decoder.decode_32bit_int()
    force = decoder.decode_32bit_int()
    power = decoder.decode_16bit_int()
    temperature = decoder.decode_8bit_int()
    voltage = decoder.decode_16bit_uint()
    errors = decoder.decode_16bit_uint()

    return register_value, position, force, power, temperature, voltage, errors
