from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


def motor_write_stream(client, slave_address, register_address, register_width, data):
    """
    Writes a value to a register in the Orca actuator using the motor write stream function.

    Args:
        client: The Modbus client object.
        slave_address (int): The Modbus slave address of the actuator.
        register_address (int): The address of the register to write to.
        register_width (int): The width of the register (1 for single, 2 for double).
        data (int): The data to write to the register.

    Returns:
        tuple: A tuple containing the shaft position, realized force, power consumption,
               temperature, voltage, errors, or None if the operation failed.
    """
    if register_width == 1:
        data = [0, 0, data]  # Pad with zeros if single-width register
    else:
        data = [data]

    request = client.write_registers(
        1,
        [register_address, register_width] + data,
        unit=slave_address,
        function_code=105,  # Custom function code 105 (0x69)
    )
    if request.isError():
        print(f"Error sending motor write stream: {request}")
        return None

    response = client.read_holding_registers(
        1, 6, unit=slave_address, function_code=105
    )
    if response.isError():
        print(f"Error reading motor write stream response: {response}")
        return None

    decoder = BinaryPayloadDecoder.fromRegisters(
        response.registers, byteorder=Endian.BIG
    )
    position = decoder.decode_32bit_int()
    force = decoder.decode_32bit_int()
    power = decoder.decode_16bit_int()
    temperature = decoder.decode_8bit_int()
    voltage = decoder.decode_16bit_uint()
    errors = decoder.decode_16bit_uint()

    return position, force, power, temperature, voltage, errors
