from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


def motor_command_stream(client, slave_address, sub_function_code, data):
    """
    Sends a motor command stream message to the Orca actuator.

    Args:
        client: The Modbus client object.
        slave_address (int): The Modbus slave address of the actuator.
        sub_function_code (int): The sub-function code specifying the desired operation mode.
        data (int or list): The data associated with the command (e.g., force or position target).

    Returns:
        tuple: A tuple containing the shaft position, realized force, power consumption,
               temperature, voltage, errors, or None if the operation failed.
    """
    if isinstance(data, int):
        data = [data]
    request = client.write_registers(
        1,
        [sub_function_code] + data,
        unit=slave_address,
        function_code=100,  # Custom function code 100 (0x64)
    )
    if request.isError():
        print(f"Error sending motor command stream: {request}")
        return None

    response = client.read_holding_registers(
        1, 6, unit=slave_address, function_code=100
    )
    if response.isError():
        print(f"Error reading motor command stream response: {response}")
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
